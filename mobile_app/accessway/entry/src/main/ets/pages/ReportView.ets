import { common } from '@kit.AbilityKit';
import { util } from '@kit.ArkTS';
import { appModel, errorText } from '../data/AppModel';
import { currentPosition } from '../data/Location';
import { ErrorCode, RepoError } from '../data/Repository';
import { NearbyFact } from '../domain/Facts';
import { formatDistance } from '../domain/Geo';
import { tr } from '../model/I18n';
import {
  alreadyReported,
  categoryLabel,
  countSteps,
  factTitle,
  formatDate,
  kindLabel,
  kindShort,
  otherAnswer,
  sameQuestion,
  streetLabel
} from '../model/Labels';
import { AMENITY_KINDS, BARRIER_KINDS, Fact, FactCategory, FactKind } from '../model/Types';
import { KindIcon } from '../components/Glyphs';
import { MapCanvas, MapMode } from '../components/MapCanvas';
import { FONT, FONT_B, fs, P, RADIUS } from '../components/Theme';
import {
  Btn,
  BtnKind,
  BoxKind,
  KeyValue,
  MessageBox,
  Segmented,
  SheetBox,
  SheetTitle,
  StatusBadge,
  StatusLine
} from '../components/Ui';
import { Nav, AppScreen } from './Nav';

const RADII: number[] = [10, 25, 50, 100];
const STEP_SAVED: number = 6;

/**
 * V-7: step-by-step reporting of a barrier, amenity or area. Before saving we show facts of the same kind
 * within 15 m, so an existing one can be confirmed instead of adding a duplicate.
 */
@Component
export struct ReportView {
  nav: Nav = new Nav();
  @State step: number = 1;
  @State category: FactCategory = FactCategory.BARRIER;
  @State kind: FactKind = FactKind.STEPS;
  @State lat: number = NaN;
  @State lon: number = NaN;
  @State street: string = '';
  @State stepCount: string = '';
  @State description: string = '';
  @State radius: number = 25;
  @State nearby: NearbyFact[] = [];
  @State saved: Fact | null = null;
  @State error: string = '';
  @State busy: boolean = false;
  private saveKey: string = '';
  private saveContent: string = '';

  private isArea(): boolean {
    return this.category === FactCategory.AREA;
  }

  private total(): number {
    return this.isArea() ? 4 : 5;
  }

  private stepLabel(): string {
    const shown = this.isArea() && this.step === 5 ? 4 : this.step;
    return tr(`Krok ${shown} z ${this.total()}`, `Step ${shown} of ${this.total()}`);
  }

  private kinds(): FactKind[] {
    return this.category === FactCategory.AMENITY ? AMENITY_KINDS : BARRIER_KINDS;
  }

  private chooseCategory(c: FactCategory): void {
    this.category = c;
    this.kind = c === FactCategory.AMENITY ? FactKind.ELEVATOR : (c === FactCategory.AREA ? FactKind.ROUGH_SURFACE :
      FactKind.STEPS);
  }

  private async setPoint(): Promise<void> {
    this.lat = appModel.mapLat;
    this.lon = appModel.mapLon;
    this.street = await appModel.repo.geocoding.streetAt(this.lat, this.lon);
    appModel.fitTo(this.lat, this.lon, 70);
    this.step = 3;
  }

  private async afterDetails(): Promise<void> {
    if (this.isArea()) {
      appModel.fitTo(this.lat, this.lon, Math.max(70, this.radius * 2.5));
      this.step = 5;
      return;
    }
    try {
      this.nearby = await appModel.repo.facts.findNearby(this.kind, false, this.lat, this.lon);
    } catch (e) {
      this.error = errorText(e as Object);
      return;
    }
    appModel.fitTo(this.lat, this.lon, 45);
    this.step = this.nearby.length > 0 ? 4 : 5;
  }

  private stepsNumber(): number {
    const n = parseInt(this.stepCount.trim(), 10);
    return isNaN(n) || n <= 0 ? 0 : Math.min(n, 999);
  }

  /**
   * The idempotency key of the summary being saved: generated once for an approved summary and kept for every
   * retry of the same content; a changed summary gets a new key.
   */
  private keyFor(content: string): string {
    if (this.saveContent !== content || this.saveKey.length === 0) {
      this.saveContent = content;
      this.saveKey = util.generateRandomUUID(true);
    }
    return this.saveKey;
  }

  private async save(): Promise<void> {
    this.busy = true;
    this.error = '';
    const content = [this.kind, this.isArea(), this.lat, this.lon, this.radius,
      this.kind === FactKind.STEPS ? this.stepsNumber() : 0, this.description.trim()].join('|');
    try {
      this.saved = await appModel.repo.facts.report({
        idempotencyKey: this.keyFor(content),
        kind: this.kind,
        isArea: this.isArea(),
        lat: this.lat,
        lon: this.lon,
        radiusM: this.radius,
        stepCount: this.kind === FactKind.STEPS ? this.stepsNumber() : 0,
        description: this.description
      });
      await appModel.refreshFacts();
      if (appModel.plan !== null) {
        await appModel.computeRoute();
      }
      appModel.fitTo(this.lat, this.lon, 120);
      this.step = STEP_SAVED;
    } catch (e) {
      this.error = errorText(e as Object);
    }
    this.busy = false;
  }

  private async same(f: Fact): Promise<void> {
    try {
      await appModel.repo.facts.vote(f.id, true);
      await appModel.refreshFacts();
    } catch (e) {
      if (!(e instanceof RepoError) || (e as RepoError).code !== ErrorCode.VOTE_TOO_SOON) {
        this.error = errorText(e as Object);
        return;
      }
    }
    this.nav.replace(AppScreen.FACT, f.id);
  }

  private async locate(): Promise<void> {
    try {
      const p = await currentPosition(this.getUIContext().getHostContext() as common.UIAbilityContext);
      appModel.mapLat = p.lat;
      appModel.mapLon = p.lon;
      this.step = 2;
      this.nav.refresh();
    } catch (e) {
      this.error = errorText(e as Object);
    }
  }

  private restart(): void {
    this.step = 1;
    this.saved = null;
    this.description = '';
    this.stepCount = '';
    this.lat = NaN;
    this.lon = NaN;
    this.chooseCategory(FactCategory.BARRIER);
  }

  private mapHeight(): number {
    if (this.step === 2) {
      return 370;
    }
    if (this.step === 3) {
      return 135;
    }
    if (this.step === 1) {
      return 250;
    }
    return 190;
  }

  private mapFacts(): Fact[] {
    if (this.step === 4) {
      const out: Fact[] = [];
      for (const n of this.nearby) {
        out.push(n.fact);
      }
      return out;
    }
    if (this.step === STEP_SAVED && this.saved !== null) {
      return [this.saved as Fact];
    }
    return [];
  }

  build() {
    Scroll() {
      Column() {
        ForEach([this.step], (st: number) => {
          this.map()
        }, (st: number) => `${st}-${this.radius}-${this.lat}`)
        SheetBox() {
          if (this.step === 1) {
            this.stepKind()
          } else if (this.step === 2) {
            this.stepPlace()
          } else if (this.step === 3) {
            this.stepDetails()
          } else if (this.step === 4) {
            this.stepExisting()
          } else if (this.step === 5) {
            this.stepSummary()
          } else {
            this.stepSaved()
          }
        }
      }
      .width('100%')
    }
    .width('100%')
    .height('100%')
    .align(Alignment.Top)
    .edgeEffect(EdgeEffect.None)
    .backgroundColor(P().card)
  }

  @Builder
  map() {
    MapCanvas({
      mapHeight: this.mapHeight(),
      mode: this.step === 2 ? MapMode.PICK : MapMode.PLAIN,
      showLocate: this.step === 2,
      onLocate: () => {
        this.locate();
      },
      facts: this.mapFacts(),
      pointLat: this.step >= 3 && this.step < STEP_SAVED ? this.lat : NaN,
      pointLon: this.lon,
      pointRadiusM: this.step === 4 ? 15 : 0,
      areaRadiusM: this.isArea() && this.step >= 3 && this.step < STEP_SAVED ? this.radius : 0
    })
  }

  @Builder
  buttons(back: string, next: string, onBack: () => void, onNext: () => void, nextEnabled: boolean) {
    if (this.error.length > 0) {
      MessageBox({ text: this.error, kind: BoxKind.ERROR }).margin({ top: 10 })
    }
    Row({ space: 10 }) {
      Btn({ label: back, kind: BtnKind.OUTLINE, action: onBack }).layoutWeight(1)
      Btn({ label: next, enabledState: nextEnabled && !this.busy, action: onNext }).layoutWeight(1)
    }
    .width('100%')
    .margin({ top: 16 })
  }

  @Builder
  radioRow(selected: boolean, title: string, sub: string, kind: FactKind, glyph: boolean, onPick: () => void) {
    Row({ space: 12 }) {
      Radio({ value: title, group: 'report' })
        .checked(selected)
        .radioStyle({ checkedBackgroundColor: P().primary, uncheckedBorderColor: P().textVar })
        .width(22)
        .height(22)
        .accessibilityText(title)
        .onChange((v: boolean) => {
          if (v) {
            onPick();
          }
        })
      if (glyph) {
        KindIcon({ kind: kind, category: FactCategory.BARRIER, iconSize: 18, color: P().text })
      }
      Column({ space: 2 }) {
        Text(title).fontFamily(FONT).fontSize(fs(15)).fontColor(P().text)
        if (sub.length > 0) {
          Text(sub).fontFamily(FONT).fontSize(fs(12.5)).fontColor(P().textVar)
        }
      }
      .alignItems(HorizontalAlign.Start)
      .layoutWeight(1)
    }
    .width('100%')
    .constraintSize({ minHeight: 48 })
    .padding({ top: 8, bottom: 8 })
    .border({ width: { bottom: 1 }, color: P().outlineVar })
    .onClick(onPick)
  }

  @Builder
  stepKind() {
    SheetTitle({ step: this.stepLabel(), title: tr('Co zgłaszasz?', 'What are you reporting?'),
      onClose: () => this.nav.home() })
    Divider().color(P().outlineVar).margin({ top: 8 })
    this.radioRow(this.category === FactCategory.BARRIER, tr('Barierę', 'A barrier'),
      tr('schody, wysoki krawężnik, zła nawierzchnia, strome nachylenie, wąskie przejście',
        'stairs, high kerb, poor surface, steep incline, narrow passage'), FactKind.STEPS, false,
      () => this.chooseCategory(FactCategory.BARRIER))
    this.radioRow(this.category === FactCategory.AMENITY, tr('Udogodnienie', 'An amenity'),
      tr('rampa, winda, obniżony krawężnik, dostępna toaleta, miejsce odpoczynku, poręcz',
        'ramp, elevator, lowered kerb, accessible toilet, rest place, handrail'), FactKind.RAMP, false,
      () => this.chooseCategory(FactCategory.AMENITY))
    this.radioRow(this.category === FactCategory.AREA, tr('Obszar', 'An area'),
      tr('większy niedostępny fragment, na przykład remont chodnika', 'a larger inaccessible stretch, for example sidewalk works'),
      FactKind.ROUGH_SURFACE, false, () => this.chooseCategory(FactCategory.AREA))
    this.buttons(tr('Anuluj', 'Cancel'), tr('Dalej', 'Next'), () => this.nav.home(), () => {
      this.step = 2;
    }, true)
  }

  @Builder
  stepPlace() {
    SheetTitle({
      step: this.stepLabel(),
      title: this.category === FactCategory.AMENITY ? tr('Wskaż miejsce udogodnienia', 'Point at the amenity') :
        (this.isArea() ? tr('Wskaż środek obszaru', 'Point at the middle of the area') :
          tr('Wskaż miejsce bariery', 'Point at the barrier')),
      onClose: () => this.nav.home()
    })
    Text(tr('Przesuń mapę, aż znacznik na środku wskaże to miejsce. Na klawiaturze przesuwasz mapę strzałkami.',
      'Move the map until the marker in the middle points at the place. With a keyboard, move the map with the arrow keys.'))
      .fontFamily(FONT).fontSize(fs(13.5)).fontColor(P().textVar).margin({ top: 6 })
    Text(tr('Przycisk Moja lokalizacja tylko przesuwa mapę na tym urządzeniu. Zapisujemy punkt, który ustawisz, a nie Twoje położenie.',
      'The My location button only moves the map on this device. We save the point you set, not your position.'))
      .fontFamily(FONT).fontSize(fs(12.5)).fontColor(P().textVar).margin({ top: 8 })
    this.buttons(tr('Wróć', 'Back'), tr('Ustaw ten punkt', 'Set this point'), () => {
      this.step = 1;
    }, () => {
      this.setPoint();
    }, true)
  }

  @Builder
  stepDetails() {
    SheetTitle({
      step: this.stepLabel(),
      title: this.category === FactCategory.AMENITY ? tr('Jakie to udogodnienie?', 'What amenity is it?') :
        (this.isArea() ? tr('Jaki to obszar?', 'What area is it?') : tr('Jaka to bariera?', 'What barrier is it?')),
      onClose: () => this.nav.home()
    })
    if (this.isArea()) {
      Text(tr('Promień obszaru', 'Area radius')).fontFamily(FONT_B).fontSize(fs(13)).fontColor(P().text)
        .margin({ top: 10, bottom: 6 })
      Segmented({
        options: RADII.map((r: number): string => `${r} m`),
        selected: RADII.indexOf(this.radius),
        onSelect: (i: number) => {
          this.radius = RADII[i];
        }
      })
      Text(tr('Co utrudnia przejście?', 'What makes it hard to pass?')).fontFamily(FONT_B).fontSize(fs(13))
        .fontColor(P().text).margin({ top: 14 })
    }
    Divider().color(P().outlineVar).margin({ top: 8 })
    ForEach(this.kinds(), (k: FactKind) => {
      this.radioRow(this.kind === k, kindLabel(k), '', k, true, () => {
        this.kind = k;
      })
    }, (k: FactKind) => `${k}-${this.kind === k}`)
    if (this.kind === FactKind.STEPS && !this.isArea()) {
      Text() {
        Span(tr('Liczba stopni ', 'Number of steps ')).fontFamily(FONT_B)
        Span(tr('(opcjonalnie)', '(optional)')).fontFamily(FONT).fontColor(P().textVar)
      }
      .fontSize(fs(13)).fontColor(P().text).margin({ top: 14, bottom: 6 })
      TextInput({ text: this.stepCount })
        .type(InputType.Number)
        .fontFamily(FONT).fontSize(fs(15))
        .width(120).height(46)
        .borderRadius(RADIUS).backgroundColor(P().card).border({ width: 1, color: P().textVar })
        .accessibilityText(tr('Liczba stopni, opcjonalnie', 'Number of steps, optional'))
        .onChange((v: string) => {
          this.stepCount = v;
        })
    }
    Text() {
      Span(tr('Opis ', 'Description ')).fontFamily(FONT_B)
      Span(tr('(opcjonalnie)', '(optional)')).fontFamily(FONT).fontColor(P().textVar)
    }
    .fontSize(fs(13)).fontColor(P().text).margin({ top: 14, bottom: 6 })
    TextArea({ text: this.description })
      .fontFamily(FONT).fontSize(fs(14.5))
      .width('100%').height(84)
      .borderRadius(RADIUS).backgroundColor(P().card).border({ width: 1, color: P().textVar })
      .maxLength(500)
      .accessibilityText(tr('Opis, opcjonalnie', 'Description, optional'))
      .onChange((v: string) => {
        this.description = v;
      })
    Text(tr('Opis jest publiczny. Nie podawaj danych osób.', 'The description is public. Do not give anyone\'s personal data.'))
      .fontFamily(FONT).fontSize(fs(12)).fontColor(P().textVar).margin({ top: 6 })
    this.buttons(tr('Wróć', 'Back'), tr('Dalej', 'Next'), () => {
      this.step = 2;
    }, () => {
      this.afterDetails();
    }, true)
  }

  @Builder
  stepExisting() {
    SheetTitle({ step: this.stepLabel(), title: sameQuestion(this.kind), onClose: () => this.nav.home() })
    Text(tr(`W promieniu około 15 m od Twojego punktu ${alreadyReported(this.kind)}. Jeśli to te same, potwierdzisz istniejący fakt zamiast dodawać nowy.`,
      `Within about 15 m of your point ${alreadyReported(this.kind)}. If it is the same, you confirm the existing fact instead of adding a new one.`))
      .fontFamily(FONT).fontSize(fs(13.5)).fontColor(P().textVar).margin({ top: 6, bottom: 4 })
    ForEach(this.nearby, (n: NearbyFact) => {
      Row({ space: 12 }) {
        KindIcon({ kind: n.fact.kind, category: n.fact.category, iconSize: 20, color: P().text })
        Column({ space: 4 }) {
          Row() {
            Text(factTitle(n.fact.kind, n.fact.category, n.fact.stepCount, n.fact.radiusM))
              .fontFamily(FONT_B).fontSize(fs(15)).fontColor(P().text).layoutWeight(1)
            Text(tr(`${formatDistance(n.distanceM)} stąd`, `${formatDistance(n.distanceM)} away`))
              .fontFamily(FONT_B).fontSize(fs(13.5)).fontColor(P().text)
          }
          .width('100%')
          if (n.fact.street.length > 0) {
            Text(streetLabel(n.fact.street)).fontFamily(FONT).fontSize(fs(13)).fontColor(P().textVar)
          }
          StatusLine({ fact: n.fact })
          Btn({ label: tr('To te same', 'It is the same'), kind: BtnKind.OUTLINE, small: true, action: () => {
            this.same(n.fact);
          } }).margin({ top: 4 })
        }
        .alignItems(HorizontalAlign.Start)
        .layoutWeight(1)
      }
      .width('100%')
      .alignItems(VerticalAlign.Top)
      .padding({ top: 12, bottom: 12 })
      .border({ width: { top: 1 }, color: P().outlineVar })
    }, (n: NearbyFact) => n.fact.id)
    this.buttons(tr('Wróć', 'Back'), otherAnswer(this.kind), () => {
      this.step = 3;
    }, () => {
      this.step = 5;
    }, true)
  }

  private placeText(): string {
    const s = streetLabel(this.street);
    return s.length > 0 ? tr(`${s}, punkt na mapie powyżej`, `${s}, the point on the map above`) :
      tr('punkt na mapie powyżej', 'the point on the map above');
  }

  @Builder
  stepSummary() {
    SheetTitle({ step: this.stepLabel(), title: tr('Sprawdź zgłoszenie', 'Check the report'), onClose: () => this.nav.home() })
    Column() {
      KeyValue({ name: tr('Rodzaj', 'Kind'), value: categoryLabel(this.category), keyWidth: 96 })
      KeyValue({ name: tr('Typ', 'Type'), value: kindShort(this.kind), keyWidth: 96 })
      if (this.isArea()) {
        KeyValue({ name: tr('Promień', 'Radius'), value: `${this.radius} m`, keyWidth: 96 })
      }
      if (this.kind === FactKind.STEPS && !this.isArea() && this.stepsNumber() > 0) {
        KeyValue({ name: tr('Liczba stopni', 'Steps'), value: `${this.stepsNumber()}`, keyWidth: 96 })
      }
      KeyValue({ name: tr('Miejsce', 'Place'), value: this.placeText(), keyWidth: 96 })
      if (this.description.trim().length > 0) {
        KeyValue({ name: tr('Opis', 'Description'), value: this.description.trim(), keyWidth: 96 })
      }
    }
    .width('100%')
    .margin({ top: 10 })
    MessageBox({
      text: tr('Po zapisaniu nikt nie zmieni tego zgłoszenia, Ty też nie. Inni zobaczą je bez żadnej informacji o autorze.',
        'After saving, nobody can change this report, you neither. Others will see it without any information about the author.'),
      kind: BoxKind.INFO
    }).margin({ top: 12 })
    this.buttons(tr('Wróć', 'Back'), tr('Zapisz zgłoszenie', 'Save the report'), () => {
      this.step = this.isArea() ? 3 : (this.nearby.length > 0 ? 4 : 3);
    }, () => {
      this.save();
    }, true)
  }

  private savedSummary(f: Fact): string {
    const title = factTitle(f.kind, f.category, f.stepCount, f.radiusM);
    const s = streetLabel(f.street);
    const where = s.length > 0 ? `${title}, ${s}.` : `${title}.`;
    return tr(`${where} ${f.kind === FactKind.STEPS && f.category !== FactCategory.AREA ? 'Są' : 'Jest'} już na mapie.`,
      `${where} It is on the map now.`);
  }

  @Builder
  stepSaved() {
    if (this.saved !== null) {
      SheetTitle({ title: tr('Zgłoszenie zapisane', 'Report saved'), showClose: false })
      Text(this.savedSummary(this.saved as Fact)).fontFamily(FONT).fontSize(fs(13.5)).fontColor(P().textVar)
        .margin({ top: 4 })
      Column() {
        KeyValue({ name: tr('Źródło', 'Source'), value: tr('zgłoszenie użytkownika', 'user report'), keyWidth: 96 })
        KeyValue({ name: tr('Zgłoszono', 'Reported'), value: formatDate((this.saved as Fact).date), keyWidth: 96 })
        Row() {
          Text(tr('Status', 'Status')).fontFamily(FONT).fontSize(fs(13.5)).fontColor(P().textVar).width(96)
          StatusBadge({ status: (this.saved as Fact).status })
        }
        .width('100%')
        .padding({ top: 4, bottom: 4 })
      }
      .width('100%')
      .margin({ top: 10 })
      MessageBox({
        text: tr('Inni mogą teraz potwierdzić, że to nadal tu jest, albo zgłosić, że tego już nie ma. Od tego zależy status.',
          'Others can now confirm that it is still there, or report that it is gone. The status depends on that.'),
        kind: BoxKind.INFO
      }).margin({ top: 12 })
      Row({ space: 10 }) {
        Btn({ label: tr('Zgłoś kolejne', 'Report another'), kind: BtnKind.OUTLINE, action: () => this.restart() })
          .layoutWeight(1)
        Btn({ label: tr('Wróć do mapy', 'Back to the map'), action: () => this.nav.home() }).layoutWeight(1)
      }
      .width('100%')
      .margin({ top: 16 })
    }
  }
}
