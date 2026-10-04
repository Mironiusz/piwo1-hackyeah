import { appModel, Endpoint } from '../data/AppModel';
import { RouteAlternative, RouteFactItem, RouteGap, RoutePlan } from '../data/Repository';
import { formatDistance, formatKm, formatKmRange } from '../domain/Geo';
import { tr } from '../model/I18n';
import { countBarriers, countSegments, formatDate, isAmenity, kindShort, plural, statusLabel, streetLabel } from '../model/Labels';
import { EdgeState, Fact, FactCategory, FactKind, FactSource, FactStatus } from '../model/Types';
import { LegendSwatch, MapCanvas } from '../components/MapCanvas';
import { DiagramStop, RouteDiagram } from '../components/RouteDiagram';
import { FONT, FONT_B, FONT_NUM, fs, P, RADIUS } from '../components/Theme';
import { Btn, BtnKind, BoxKind, FactRow, GroupHeader, Icon, LinkText, MessageBox, SheetBox } from '../components/Ui';
import { Nav, AppScreen } from './Nav';

function shortName(e: Endpoint | null): string {
  if (e === null) {
    return '';
  }
  return e.label.split(',')[0];
}

function numberWord(n: number): string {
  const pl: string[] = ['zero', 'jedna', 'dwie', 'trzy', 'cztery'];
  const en: string[] = ['zero', 'one', 'two', 'three', 'four'];
  return n < 5 ? tr(pl[n], en[n]) : `${n}`;
}

/** V-5: wynik trasy, z wariantami bez oceny (potrzeby bez barier) i bez trasy wolnej od barier z potrzeb. */
@Component
export struct RouteView {
  nav: Nav = new Nav();

  aboutToAppear(): void {
    const p = appModel.plan;
    if (p !== null && appModel.fitBox.length === 0) {
      appModel.fitBox = [p.minLat, p.maxLat, p.minLon, p.maxLon];
    }
  }

  private plan(): RoutePlan {
    return appModel.plan as RoutePlan;
  }

  private fromNeeds(): RouteFactItem[] {
    return this.plan().facts.filter((it: RouteFactItem) => !isAmenity(it.fact.kind) &&
      appModel.needs.avoid.indexOf(it.fact.kind) >= 0);
  }

  private extra(): RouteFactItem[] {
    return this.plan().facts.filter((it: RouteFactItem) => !isAmenity(it.fact.kind) &&
      (!this.plan().rated || appModel.needs.avoid.indexOf(it.fact.kind) < 0));
  }

  private amenities(): RouteFactItem[] {
    return this.plan().facts.filter((it: RouteFactItem) => isAmenity(it.fact.kind) &&
      it.fact.category !== FactCategory.AREA && appModel.needs.need.indexOf(it.fact.kind) >= 0);
  }

  private mapFacts(): Fact[] {
    const out: Fact[] = [];
    for (const it of this.plan().facts) {
      if (isAmenity(it.fact.kind) && appModel.needs.need.indexOf(it.fact.kind) < 0) {
        continue;
      }
      out.push(it.fact);
    }
    return out;
  }

  private stops(): DiagramStop[] {
    const out: DiagramStop[] = [];
    for (const it of this.fromNeeds()) {
      out.push({ atM: it.atM, label: kindShort(it.fact.kind) });
    }
    return out;
  }

  private alternativeFor(id: string): RouteAlternative | null {
    for (const a of this.plan().alternatives) {
      if (a.factId === id) {
        return a;
      }
    }
    return null;
  }

  private async showAlternative(id: string): Promise<void> {
    appModel.avoidFactIds = appModel.avoidFactIds.concat([id]);
    await appModel.computeRoute();
    this.nav.refresh();
  }

  private async resetAlternative(): Promise<void> {
    appModel.avoidFactIds = [];
    await appModel.computeRoute();
    this.nav.refresh();
  }

  private blocking(): RouteFactItem[] {
    return this.fromNeeds().filter((it: RouteFactItem) => it.fact.status === FactStatus.CONFIRMED ||
      it.fact.source === FactSource.OSM);
  }

  /** Rodzaje barier z potrzeb, przez które trasa musi przejść, gdy trasy wolnej od nich nie ma. */
  private blockingKinds(): string {
    const kinds: string[] = [];
    for (const it of this.blocking()) {
      const k = kindShort(it.fact.kind);
      if (kinds.indexOf(k) < 0) {
        kinds.push(k);
      }
    }
    return kinds.join(tr(' albo ', ' or '));
  }

  build() {
    Scroll() {
      Column() {
        if (appModel.plan === null) {
          MessageBox({ text: tr('Nie ma wyznaczonej trasy.', 'No route is planned.'), kind: BoxKind.INFO }).margin(16)
        } else {
          this.top()
          MapCanvas({
            mapHeight: 250,
            showRoute: true,
            showA: true,
            showB: true,
            facts: this.mapFacts(),
            onFactTap: (id: string) => this.nav.go(AppScreen.FACT, id)
          })
          SheetBox() {
            this.sheet()
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
  top() {
    Column({ space: 12 }) {
      Row() {
        Button({ type: ButtonType.Normal }) {
          Row({ space: 8 }) {
            Icon({ name: 'tune', iconSize: 18, color: P().onYellow })
            Text(appModel.needs.avoid.length > 0 ?
              tr(`Potrzeby: ${countBarriers(appModel.needs.avoid.length)}`, `Needs: ${countBarriers(appModel.needs.avoid.length)}`) :
              tr('Potrzeby: brak barier', 'Needs: no barriers'))
              .fontFamily(FONT_B).fontSize(fs(13.5)).fontColor(P().onYellow)
            Icon({ name: 'chevron_right', iconSize: 18, color: P().onYellow })
          }
          .padding({ left: 12, right: 8 })
        }
        .height(36)
        .borderRadius(RADIUS)
        .backgroundColor(P().yellow)
        .onClick(() => this.nav.go(AppScreen.NEEDS, 'route'))
        Blank()
        Button(tr('Zmień trasę', 'Change route'))
          .type(ButtonType.Normal)
          .fontFamily(FONT_B).fontSize(fs(13)).fontColor('#FFFFFF')
          .backgroundColor(Color.Transparent)
          .borderRadius(RADIUS)
          .border({ width: 1.5, color: '#FFFFFF' })
          .height(36)
          .padding({ left: 10, right: 10 })
          .onClick(() => this.nav.go(AppScreen.PLAN, ''))
      }
      .width('100%')
      Column() {
        RouteDiagram({
          segments: this.plan().segments,
          stops: this.stops(),
          totalM: this.plan().lengthM,
          rated: this.plan().rated,
          startName: shortName(appModel.start),
          endName: shortName(appModel.dest)
        })
      }
      .width('100%')
      .padding({ left: 12, right: 12, top: 8, bottom: 10 })
      .backgroundColor(P().card)
      .borderRadius(RADIUS)
      Row({ space: 8 }) {
        if (this.plan().rated) {
          this.tile(`${this.fromNeeds().length}`, tr(`${plural(this.fromNeeds().length, 'bariera', 'bariery', 'barier')} z potrzeb`,
            `${this.fromNeeds().length === 1 ? 'barrier' : 'barriers'} from your needs`), 'yellow')
          this.tile(formatDistance(this.plan().noDataM), tr('bez danych', 'no data'), 'dashed')
        } else {
          this.tile(tr('bez oceny', 'not rated'), tr('potrzeby nie mają żadnej bariery', 'your needs have no barrier'),
            'dashed')
        }
        this.tile(formatKm(this.plan().lengthM), tr('cała trasa', 'whole route'), 'plain')
      }
      .width('100%')
    }
    .width('100%')
    .padding({ left: 16, right: 16, top: 10, bottom: 14 })
    .backgroundColor(P().primary)
  }

  @Builder
  tile(value: string, caption: string, style: string) {
    Column({ space: 2 }) {
      Text(value).fontFamily(FONT_NUM).fontSize(fs(24))
        .fontColor(style === 'yellow' && this.fromNeeds().length > 0 ? P().yellow : '#FFFFFF')
      Text(caption).fontFamily(FONT).fontSize(fs(11.5)).fontColor('#D9FFFFFF').maxLines(2)
    }
    .layoutWeight(style === 'dashed' && !this.plan().rated ? 2 : 1)
    .height(64)
    .padding({ left: 10, right: 6, top: 6 })
    .alignItems(HorizontalAlign.Start)
    .borderRadius(RADIUS)
    .border({
      width: style === 'yellow' ? 1.5 : 1,
      color: style === 'yellow' ? P().yellow : '#B3FFFFFF',
      style: style === 'dashed' ? BorderStyle.Dashed : BorderStyle.Solid
    })
    .accessibilityGroup(true)
    .accessibilityText(`${value} ${caption}`)
  }

  @Builder
  legendItem(s: EdgeState, text: string) {
    Row({ space: 8 }) {
      LegendSwatch({ state: s })
      Text(text).fontFamily(FONT).fontSize(fs(12.5)).fontColor(P().text).layoutWeight(1)
    }
    .layoutWeight(1)
  }

  @Builder
  legend() {
    if (this.plan().rated) {
      Column({ space: 8 }) {
        Row({ space: 10 }) {
          this.legendItem(EdgeState.BARRIER, tr('bariera z potrzeb', 'barrier from your needs'))
          this.legendItem(EdgeState.CLEAR, tr('bez barier, dane pełne', 'no barriers, full data'))
        }
        .width('100%')
        Row({ space: 10 }) {
          this.legendItem(EdgeState.PARTIAL, tr('dane niepełne', 'incomplete data'))
          this.legendItem(EdgeState.NO_DATA, tr('brak danych', 'no data'))
        }
        .width('100%')
      }
      .width('100%')
      .margin({ top: 12 })
    } else {
      Row({ space: 8 }) {
        LegendSwatch({ unrated: true })
        Text(tr('trasa bez oceny odcinków', 'route without segment rating'))
          .fontFamily(FONT).fontSize(fs(12.5)).fontColor(P().text)
      }
      .margin({ top: 14 })
    }
    Row({ space: 4 }) {
      Text(tr(`Dane OpenStreetMap z dnia ${formatDate(appModel.info().osmDate)}.`,
        `OpenStreetMap data from ${formatDate(appModel.info().osmDate)}.`))
        .fontFamily(FONT).fontSize(fs(12)).fontColor(P().textVar)
      LinkText({ label: tr('O danych', 'About the data'), textSize: 12, action: () => this.nav.go(AppScreen.ABOUT, '') })
    }
    .width('100%')
    .margin({ top: 8 })
    .padding({ bottom: 6 })
    .border({ width: { bottom: 1 }, color: P().outlineVar })
  }

  @Builder
  sheet() {
    if (!this.plan().rated) {
      MessageBox({
        lead: tr('Nie oceniamy odcinków tej trasy,', 'We do not rate the segments of this route,'),
        text: tr('bo Twoje potrzeby nie zawierają żadnej bariery. To nie znaczy, że trasa jest wolna od barier: znane bariery są na liście niżej.',
          'because your needs contain no barrier. This does not mean the route is free of barriers: known barriers are in the list below.'),
        kind: BoxKind.ERROR
      }).margin({ top: 6 })
      Btn({ label: tr('Ustaw potrzeby', 'Set your needs'), action: () => this.nav.go(AppScreen.NEEDS, 'route') })
        .margin({ top: 12 })
    } else if (!this.plan().barrierFree) {
      MessageBox({
        lead: tr('Nie ma trasy bez barier z Twoich potrzeb.', 'There is no route without barriers from your needs.'),
        text: this.blockingKinds().length > 0 ?
          tr(`Każda droga do tego celu prowadzi przez ${this.blockingKinds()}. Pokazujemy trasę, na której takich barier jest najmniej: ${numberWord(this.blocking().length)}.`,
            `Every way to this destination goes through ${this.blockingKinds()}. We show the route with the fewest such barriers: ${numberWord(this.blocking().length)}.`) :
          tr('Każda droga do tego celu prowadzi przez barierę z Twoich potrzeb. Pokazujemy trasę, na której takich barier jest najmniej.',
            'Every way to this destination goes through a barrier from your needs. We show the route with the fewest such barriers.'),
        kind: BoxKind.ERROR
      }).margin({ top: 6 })
    }
    if (appModel.avoidFactIds.length > 0) {
      MessageBox({
        lead: tr('Pokazujemy trasę alternatywną.', 'Showing the alternative route.'),
        text: tr('Omija niezweryfikowaną barierę z Twoich potrzeb.', 'It avoids an unverified barrier from your needs.'),
        kind: BoxKind.INFO
      }).margin({ top: 8 })
      LinkText({ label: tr('Wróć do pierwszej trasy', 'Back to the first route'), action: () => {
        this.resetAlternative();
      } })
    }
    this.legend()
    if (this.plan().rated) {
      this.ratedGroups()
    } else {
      this.unratedGroups()
    }
  }

  @Builder
  row(it: RouteFactItem, line: boolean) {
    FactRow({ fact: it.fact, distanceText: formatKm(it.atM), showLine: line,
      onOpen: (id: string) => this.nav.go(AppScreen.FACT, id) })
  }

  @Builder
  ratedGroups() {
    GroupHeader({ title: tr('Z Twoich potrzeb', 'From your needs'), count: `${this.fromNeeds().length}` })
    if (this.fromNeeds().length === 0) {
      MessageBox({ text: tr('Na tej trasie nie znamy żadnej bariery z Twoich potrzeb.',
        'We know no barrier from your needs on this route.'), kind: BoxKind.INFO }).margin({ top: 10 })
    }
    ForEach(this.fromNeeds(), (it: RouteFactItem) => {
      Column() {
        this.row(it, this.alternativeFor(it.fact.id) === null)
        if (this.alternativeFor(it.fact.id) !== null) {
          this.altCard(it.fact, this.alternativeFor(it.fact.id) as RouteAlternative)
        }
      }
    }, (it: RouteFactItem) => it.fact.id)
    GroupHeader({ title: tr('Dodatkowe bariery', 'Other barriers'), count: this.extra().length > 0 ? `${this.extra().length}` : '' })
    if (this.extra().length === 0) {
      MessageBox({
        text: this.plan().noDataM >= 10 ?
          tr(`Nie znamy żadnych innych barier na tej trasie. ${formatDistance(this.plan().noDataM)} trasy nie ma danych.`,
            `We know no other barriers on this route. ${formatDistance(this.plan().noDataM)} of the route has no data.`) :
          tr('Nie znamy żadnych innych barier na tej trasie.', 'We know no other barriers on this route.'),
        kind: BoxKind.INFO
      }).margin({ top: 10 })
    }
    ForEach(this.extra(), (it: RouteFactItem) => {
      this.row(it, true)
    }, (it: RouteFactItem) => it.fact.id)
    this.amenityGroup()
    if (this.plan().gaps.length > 0) {
      GroupHeader({ title: tr('Czego nie wiemy', 'What we do not know'), count: countSegments(this.plan().gaps.length) })
      Column({ space: 8 }) {
        ForEach(this.plan().gaps, (g: RouteGap, i: number) => {
          this.gap(g)
        }, (g: RouteGap, i: number) => `${i}-${g.fromM}`)
      }
      .width('100%')
      .margin({ top: 10 })
    }
  }

  @Builder
  unratedGroups() {
    GroupHeader({ title: tr('Bariery na trasie', 'Barriers on the route'), count: `${this.extra().length}` })
    if (this.extra().length === 0) {
      MessageBox({ text: tr('Nie znamy żadnych barier na tej trasie. Brak informacji nie oznacza, że trasa jest dostępna.',
        'We know no barriers on this route. Missing information never means the route is accessible.'),
        kind: BoxKind.INFO }).margin({ top: 10 })
    }
    ForEach(this.extra(), (it: RouteFactItem) => {
      this.row(it, true)
    }, (it: RouteFactItem) => it.fact.id)
    this.amenityGroup()
  }

  @Builder
  amenityGroup() {
    GroupHeader({ title: tr('Udogodnienia na trasie', 'Amenities on the route'),
      count: this.amenities().length > 0 ? `${this.amenities().length}` : '' })
    if (appModel.needs.need.length === 0) {
      MessageBox({ text: tr('Twoje potrzeby nie zawierają żadnego udogodnienia, więc nie mamy czego tu pokazać.',
        'Your needs contain no amenity, so there is nothing to show here.'), kind: BoxKind.INFO }).margin({ top: 10 })
    } else if (this.amenities().length === 0) {
      MessageBox({ text: tr('Żadne udogodnienie z Twoich potrzeb nie leży bliżej niż 50 m od tej trasy.',
        'No amenity from your needs lies closer than 50 m to this route.'), kind: BoxKind.INFO }).margin({ top: 10 })
    }
    ForEach(this.amenities(), (it: RouteFactItem) => {
      this.row(it, true)
    }, (it: RouteFactItem) => it.fact.id)
  }

  @Builder
  altCard(f: Fact, a: RouteAlternative) {
    Row({ space: 10 }) {
      Text() {
        Span(tr('Trasa alternatywna', 'An alternative route')).fontFamily(FONT_B)
        Span(tr(` omija ${f.kind === FactKind.STEPS ? 'te schody' : 'tę barierę'} i jest o ${formatDistance(a.extraM)} dłuższa. Powód: ${kindShort(f.kind)}, status ${statusLabel(f.status)}.`,
          ` avoids this ${kindShort(f.kind)} and is ${formatDistance(a.extraM)} longer. Reason: ${kindShort(f.kind)}, status ${statusLabel(f.status)}.`))
          .fontFamily(FONT)
      }
      .fontSize(fs(13)).fontColor(P().text).lineHeight(fs(18)).layoutWeight(1)
      Btn({ label: tr('Pokaż', 'Show'), kind: BtnKind.OUTLINE, small: true, action: () => {
        this.showAlternative(f.id);
      } })
    }
    .width('100%')
    .padding(12)
    .margin({ bottom: 12 })
    .borderRadius(RADIUS)
    .border({ width: 1, color: P().outlineVar })
  }

  @Builder
  gap(g: RouteGap) {
    MessageBox({
      lead: g.isStart ? tr(`Start, pierwsze ${formatDistance(g.toM - g.fromM)}.`, `Start, first ${formatDistance(g.toM - g.fromM)}.`) :
        (g.isEnd ? tr(`Koniec, ostatnie ${formatDistance(g.toM - g.fromM)}.`, `End, last ${formatDistance(g.toM - g.fromM)}.`) :
          `${formatKmRange(g.fromM, g.toM)}${g.street.length > 0 ? ', ' + streetLabel(g.street) : ''}.`),
      text: (g.isStart ? tr('Odcinek od wybranego punktu do drogi. ', 'The stretch from the chosen point to the path. ') :
        (g.isEnd ? tr('Odcinek od drogi do wybranego punktu. ', 'The stretch from the path to the chosen point. ') : '')) +
        tr(`Brak danych: ${g.missing.join(', ')}.`, `No data: ${g.missing.join(', ')}.`),
      kind: BoxKind.GAP
    })
  }
}
