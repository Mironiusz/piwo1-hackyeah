import { appModel, errorText } from '../data/AppModel';
import { MyVote } from '../data/Repository';
import { formatKm } from '../domain/Geo';
import { tr } from '../model/I18n';
import { factTitle, formatDate, isAmenity, kindLabel, streetLabel } from '../model/Labels';
import { Fact, FactCategory, FactKind, FactSource } from '../model/Types';
import { MapCanvas } from '../components/MapCanvas';
import { FONT, FONT_B, fs, P } from '../components/Theme';
import {
  Btn,
  BtnKind,
  BoxKind,
  KeyValue,
  LinkText,
  MessageBox,
  SampleChip,
  SheetBox,
  SheetTitle,
  StatusBadge
} from '../components/Ui';
import { Nav } from './Nav';

/** V-6: szczegóły faktu z głosem "Nadal jest" albo "Już nie ma", sprzecznością z OSM i zgłoszeniem do moderacji. */
@Component
export struct FactView {
  nav: Nav = new Nav();
  factId: string = '';
  @State fact: Fact | null = null;
  @State myVote: MyVote | null = null;
  @State busy: boolean = false;
  @State error: string = '';
  @State flagged: boolean = false;

  aboutToAppear(): void {
    this.fact = appModel.factById(this.factId);
    const f = this.fact;
    if (f !== null) {
      appModel.fitTo(f.lat, f.lon, Math.max(110, f.radiusM * 3));
    }
    this.load();
  }

  private async load(): Promise<void> {
    try {
      this.fact = await appModel.repo.facts.getFact(this.factId);
      this.myVote = await appModel.repo.facts.myVote(this.factId);
    } catch (e) {
      this.error = errorText(e as Object);
    }
  }

  private async vote(stillThere: boolean): Promise<void> {
    this.busy = true;
    this.error = '';
    try {
      this.myVote = await appModel.repo.facts.vote(this.factId, stillThere);
      await appModel.refreshFacts();
      if (appModel.plan !== null) {
        await appModel.computeRoute();
      }
      this.fact = await appModel.repo.facts.getFact(this.factId);
    } catch (e) {
      this.error = errorText(e as Object);
    }
    this.busy = false;
  }

  private async flag(): Promise<void> {
    try {
      await appModel.repo.facts.flagForModeration(this.factId);
      this.flagged = true;
      this.nav.toast(tr('Zgłoszone do moderacji', 'Sent to moderation'));
    } catch (e) {
      this.error = errorText(e as Object);
    }
  }

  private question(f: Fact): string {
    if (f.category === FactCategory.AREA) {
      return tr('Czy ten obszar nadal jest trudny do przejścia?', 'Is this area still hard to pass?');
    }
    if (isAmenity(f.kind)) {
      return tr('Czy to udogodnienie nadal tu jest?', 'Is this amenity still here?');
    }
    return tr('Czy ta bariera nadal tu jest?', 'Is this barrier still here?');
  }

  private subtitle(f: Fact): string {
    const at = appModel.routePosition(f.id);
    const street = streetLabel(f.street);
    if (at >= 0) {
      return street.length > 0 ? tr(`${street}, ${formatKm(at)} od startu`, `${street}, ${formatKm(at)} from the start`) :
        tr(`${formatKm(at)} od startu`, `${formatKm(at)} from the start`);
    }
    return street;
  }

  private mapFacts(f: Fact): Fact[] {
    if (appModel.routePosition(f.id) >= 0 && appModel.plan !== null) {
      const out: Fact[] = [];
      for (const it of appModel.plan.facts) {
        out.push(it.fact);
      }
      return out;
    }
    return [f];
  }

  build() {
    Scroll() {
      Column() {
        if (this.fact !== null) {
          MapCanvas({
            mapHeight: 255,
            facts: this.mapFacts(this.fact as Fact),
            selectedId: this.factId,
            showRoute: appModel.routePosition(this.factId) >= 0,
            showA: appModel.routePosition(this.factId) >= 0,
            showB: appModel.routePosition(this.factId) >= 0
          })
          SheetBox() {
            this.sheet(this.fact as Fact)
          }
        } else if (this.error.length > 0) {
          MessageBox({ text: this.error, kind: BoxKind.ERROR }).margin(16)
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
  sheet(f: Fact) {
    SheetTitle({ title: factTitle(f.kind, f.category, f.stepCount, f.radiusM), onClose: () => this.nav.back() })
    if (this.subtitle(f).length > 0) {
      Text(this.subtitle(f)).fontFamily(FONT).fontSize(fs(13.5)).fontColor(P().textVar)
    }
    if (f.isSample) {
      SampleChip().margin({ top: 8 })
    }
    Column() {
      KeyValue({ name: tr('Źródło', 'Source'), value: f.source === FactSource.OSM ? 'OpenStreetMap' :
        tr('zgłoszenie użytkownika', 'user report') })
      if (f.source === FactSource.OSM) {
        KeyValue({ name: tr('Edycja w OSM', 'Edited in OSM'), value: formatDate(f.date) })
      } else if (f.lastConfirmed > f.date) {
        KeyValue({ name: tr('Ostatnio potwierdzone', 'Last confirmed'), value: formatDate(f.lastConfirmed) })
      } else {
        KeyValue({ name: tr('Zgłoszono', 'Reported'), value: formatDate(f.date) })
      }
      Row() {
        Text(tr('Status', 'Status')).fontFamily(FONT).fontSize(fs(13.5)).fontColor(P().textVar).width(132)
        StatusBadge({ status: f.status })
      }
      .width('100%')
      .padding({ top: 4, bottom: 4 })
      if (f.category === FactCategory.AREA) {
        KeyValue({ name: tr('Promień', 'Radius'), value: `${f.radiusM} m` })
      }
      if (f.description.length > 0) {
        KeyValue({ name: tr('Opis', 'Description'), value: f.description })
      }
    }
    .width('100%')
    .margin({ top: 10 })
    if (f.conflictKind.length > 0) {
      MessageBox({
        lead: tr('OpenStreetMap podaje tu co innego:', 'OpenStreetMap says something else here:'),
        text: tr(`${kindLabel(f.conflictKind as FactKind).toLowerCase()}${f.conflictDate > 0 ? ', edycja ' + formatDate(f.conflictDate) : ''}. Odcinek trasy idzie za OpenStreetMap, dopóki to zgłoszenie nie zostanie potwierdzone.`,
          `${kindLabel(f.conflictKind as FactKind).toLowerCase()}${f.conflictDate > 0 ? ', edited ' + formatDate(f.conflictDate) : ''}. The route follows OpenStreetMap until this report is confirmed.`),
        kind: BoxKind.ERROR
      }).margin({ top: 10 })
    }
    if (this.myVote !== null) {
      MessageBox({
        lead: tr(`Twój głos: ${(this.myVote as MyVote).stillThere ? 'nadal jest' : 'już nie ma'}.`,
          `Your vote: ${(this.myVote as MyVote).stillThere ? 'still there' : 'gone'}.`),
        text: tr(`Zapisaliśmy go ${formatDate((this.myVote as MyVote).at)}. Kolejny głos na ten fakt będzie możliwy po upływie doby.`,
          `We saved it on ${formatDate((this.myVote as MyVote).at)}. You can vote on this fact again after a day.`),
        kind: BoxKind.INFO
      }).margin({ top: 12 })
    } else {
      Text(this.question(f)).fontFamily(FONT_B).fontSize(fs(14)).fontColor(P().text).margin({ top: 14 })
    }
    if (this.error.length > 0) {
      MessageBox({ text: this.error, kind: BoxKind.ERROR }).margin({ top: 10 })
    }
    Row({ space: 10 }) {
      Btn({ label: tr('Nadal jest', 'Still there'), kind: this.myVote !== null ? BtnKind.GRAY : BtnKind.OUTLINE,
        enabledState: this.myVote === null && !this.busy, action: () => {
          this.vote(true);
        } }).layoutWeight(1)
      Btn({ label: tr('Już nie ma', 'Gone'), kind: this.myVote !== null ? BtnKind.GRAY : BtnKind.OUTLINE,
        enabledState: this.myVote === null && !this.busy, action: () => {
          this.vote(false);
        } }).layoutWeight(1)
    }
    .width('100%')
    .margin({ top: 10 })
    if (f.source === FactSource.REPORT) {
      if (this.flagged || f.flagged) {
        Text(tr('Zgłoszone do moderacji.', 'Sent to moderation.')).fontFamily(FONT).fontSize(fs(13))
          .fontColor(P().textVar).margin({ top: 16 })
      } else {
        LinkText({ label: tr('Zgłoś do moderacji', 'Send to moderation'), action: () => {
          this.flag();
        } }).margin({ top: 12 })
      }
    }
  }
}
