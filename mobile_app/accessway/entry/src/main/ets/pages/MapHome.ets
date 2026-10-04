import { appModel, errorText, ListFilter } from '../data/AppModel';
import { factsInView } from '../domain/Facts';
import { inNeeds } from '../domain/Needs';
import { tr } from '../model/I18n';
import { formatDate } from '../model/Labels';
import { Fact } from '../model/Types';
import { MapCanvas } from '../components/MapCanvas';
import { FONT, FONT_B, fs, P, RADIUS } from '../components/Theme';
import { BoxKind, FactRow, GroupHeader, Icon, LinkText, MessageBox, Segmented, SheetBox } from '../components/Ui';
import { Nav, AppScreen } from './Nav';

const MAP_H: number = 250;
const HALF_W_PX: number = 190;

/** V-3: mapa faktów. Wyszukiwanie celu, przełącznik "Z moich potrzeb / Wszystkie" i fakty w widocznym miejscu. */
@Component
export struct MapHome {
  nav: Nav = new Nav();
  @State tick: number = 0;

  private filtered(): Fact[] {
    return appModel.listFilter === ListFilter.ALL ? appModel.facts :
      appModel.facts.filter((f: Fact) => inNeeds(appModel.needs, f.kind));
  }

  private visible(): Fact[] {
    const all = this.filtered();
    if (appModel.mapScale <= 0) {
      return all;
    }
    const halfLat = (MAP_H / 2) / appModel.mapScale / 111320;
    const halfLon = HALF_W_PX / appModel.mapScale / (111320 * Math.cos(appModel.mapLat * Math.PI / 180));
    return factsInView(all, appModel.mapLat, appModel.mapLon, halfLat, halfLon);
  }

  /** Z serwerem fakty zależą od widocznego miejsca, więc po przesunięciu mapy pobieramy je od nowa. */
  private async reload(): Promise<void> {
    if (appModel.usesApi()) {
      try {
        await appModel.refreshFacts();
      } catch (e) {
        this.nav.toast(errorText(e as Object));
      }
    }
    this.tick++;
  }

  build() {
    Scroll() {
      Column() {
        MapCanvas({
          mapHeight: MAP_H,
          facts: this.filtered(),
          onFactTap: (id: string) => this.nav.go(AppScreen.FACT, id),
          onMoved: () => {
            this.reload();
          }
        })
        SheetBox() {
          this.sheet()
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
  sheet() {
    Row({ space: 10 }) {
      Icon({ name: 'search_outline', iconSize: 20, color: P().text })
      Text(tr('Dokąd idziesz? Wyznacz trasę', 'Where are you going? Plan a route'))
        .fontFamily(FONT_B).fontSize(fs(14.5)).fontColor(P().text).layoutWeight(1)
    }
    .width('100%')
    .height(46)
    .padding({ left: 12, right: 12 })
    .borderRadius(RADIUS)
    .border({ width: 1.5, color: P().textVar })
    .margin({ top: 4 })
    .focusable(true)
    .accessibilityGroup(true)
    .accessibilityRole(AccessibilityRoleType.BUTTON)
    .onClick(() => {
      if (appModel.dest === null) {
        this.nav.go(AppScreen.SEARCH, 'dest');
      } else {
        this.nav.go(AppScreen.PLAN, '');
      }
    })
    Segmented({
      options: [tr('Z moich potrzeb', 'From my needs'), tr('Wszystkie', 'All')],
      selected: appModel.listFilter === ListFilter.NEEDS ? 0 : 1,
      onSelect: (i: number) => {
        appModel.listFilter = i === 0 ? ListFilter.NEEDS : ListFilter.ALL;
        this.nav.refresh();
      }
    }).margin({ top: 12 })
    this.list(this.tick)
    Row({ space: 4 }) {
      Text(tr(`Dane OpenStreetMap z dnia ${formatDate(appModel.info().osmDate)}.`,
        `OpenStreetMap data from ${formatDate(appModel.info().osmDate)}.`))
        .fontFamily(FONT).fontSize(fs(12.5)).fontColor(P().textVar)
      LinkText({ label: tr('O danych', 'About the data'), textSize: 12.5, action: () => this.nav.go(AppScreen.ABOUT, '') })
    }
    .margin({ top: 14 })
  }

  @Builder
  list(tick: number) {
    GroupHeader({ title: tr('Fakty w tym miejscu', 'Facts in this area'), count: `${this.visible().length}` })
    if (appModel.listFilter === ListFilter.NEEDS && appModel.needs.avoid.length + appModel.needs.need.length === 0) {
      MessageBox({
        lead: tr('Nie masz zaznaczonych potrzeb.', 'You have no needs marked.'),
        text: tr('Przełącz na Wszystkie albo ustaw potrzeby w zakładce Potrzeby.',
          'Switch to All or set your needs in the Needs tab.'),
        kind: BoxKind.INFO
      }).margin({ top: 10 })
    } else if (appModel.factsTruncated) {
      MessageBox({
        text: tr('W tym miejscu jest więcej faktów, niż możemy pokazać naraz. Przybliż mapę.',
          'There are more facts here than we can show at once. Zoom in.'),
        kind: BoxKind.INFO
      }).margin({ top: 10 })
    } else if (this.visible().length === 0) {
      MessageBox({
        text: tr('W tym miejscu mapy nie znamy żadnego faktu. Brak informacji nie oznacza, że miejsce jest dostępne.',
          'We know no facts in this part of the map. Missing information never means a place is accessible.'),
        kind: BoxKind.GAP
      }).margin({ top: 10 })
    } else {
      ForEach(this.visible(), (f: Fact, i: number) => {
        FactRow({ fact: f, onOpen: (id: string) => this.nav.go(AppScreen.FACT, id) })
      }, (f: Fact) => `${f.id}-${f.status}-${tick}`)
    }
  }
}
