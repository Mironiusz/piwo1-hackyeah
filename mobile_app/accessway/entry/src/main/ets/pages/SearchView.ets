import { appModel, Endpoint, errorText } from '../data/AppModel';
import { GeocodeResult } from '../data/Repository';
import { tr } from '../model/I18n';
import { plural } from '../model/Labels';
import { MapCanvas } from '../components/MapCanvas';
import { FONT, FONT_B, fs, P, RADIUS } from '../components/Theme';
import { Btn, BoxKind, Icon, LinkText, MessageBox, SheetBox, SheetTitle } from '../components/Ui';
import { Nav, AppScreen } from './Nav';

/**
 * V-8: address search. We search only after Enter or the button and suggest nothing while typing;
 * a result must be picked from the list, even when there is only one.
 */
@Component
export struct SearchView {
  nav: Nav = new Nav();
  target: string = 'dest';
  @State query: string = '';
  @State results: GeocodeResult[] = [];
  @State searched: boolean = false;
  @State error: string = '';
  @State busy: boolean = false;

  private isStart(): boolean {
    return this.target === 'start';
  }

  private async search(): Promise<void> {
    const q = this.query.trim();
    if (q.length === 0) {
      return;
    }
    this.busy = true;
    this.error = '';
    try {
      this.results = await appModel.repo.geocoding.search(q);
    } catch (e) {
      this.results = [];
      this.error = errorText(e as Object);
    }
    this.searched = true;
    this.busy = false;
  }

  private choose(r: GeocodeResult): void {
    const e: Endpoint = { lat: r.lat, lon: r.lon, label: r.address.length > 0 ? `${r.name}, ${r.address.split(',')[0]}` : r.name };
    if (this.isStart()) {
      appModel.start = e;
    } else {
      appModel.dest = e;
    }
    appModel.plan = null;
    appModel.planError = '';
    this.nav.toPlan();
  }

  build() {
    Scroll() {
      Column() {
        MapCanvas({ mapHeight: 175 })
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
    SheetTitle({
      title: this.isStart() ? tr('Start: wyszukaj adres', 'Start: search an address') :
        tr('Cel: wyszukaj adres', 'Destination: search an address'),
      onClose: () => this.nav.back()
    })
    Text(tr('Adres albo nazwa miejsca w Krakowie', 'Address or place name in Kraków'))
      .fontFamily(FONT_B).fontSize(fs(13)).fontColor(P().text).margin({ top: 10, bottom: 6 })
    Row({ space: 8 }) {
      TextInput({ text: this.query, placeholder: '' })
        .fontFamily(FONT)
        .fontSize(fs(15))
        .height(46)
        .layoutWeight(1)
        .borderRadius(RADIUS)
        .backgroundColor(P().card)
        .border({ width: 1, color: P().textVar })
        .enterKeyType(EnterKeyType.Search)
        .accessibilityText(tr('Adres albo nazwa miejsca w Krakowie', 'Address or place name in Kraków'))
        .onChange((v: string) => {
          this.query = v;
        })
        .onSubmit(() => {
          this.search();
        })
      Btn({ label: tr('Szukaj', 'Search'), small: true, enabledState: !this.busy, action: () => {
        this.search();
      } }).height(46)
    }
    .width('100%')
    if (!this.searched) {
      Text(tr('Szukamy po naciśnięciu Enter albo przycisku. Niczego nie podpowiadamy w trakcie pisania.',
        'We search when you press Enter or the button. We suggest nothing while you type.'))
        .fontFamily(FONT).fontSize(fs(12.5)).fontColor(P().textVar).margin({ top: 8 })
    }
    if (this.error.length > 0) {
      MessageBox({ text: this.error, kind: BoxKind.ERROR }).margin({ top: 12 })
    } else if (this.searched && this.results.length === 0) {
      MessageBox({
        lead: tr('Nic nie znaleźliśmy w Krakowie.', 'We found nothing in Kraków.'),
        text: tr('Trasy działają tylko w granicach Krakowa. Sprawdź pisownię, wpisz samą ulicę albo samą nazwę miejsca.',
          'Routes work only within Kraków. Check the spelling, type only the street or only the place name.'),
        kind: BoxKind.ERROR
      }).margin({ top: 12 })
      Text(this.isStart() ? tr('Start nie został ustawiony. Możesz też wskazać go na mapie.',
        'The start is not set. You can also pick it on the map.') :
        tr('Cel nie został ustawiony. Możesz też wskazać go na mapie.',
          'The destination is not set. You can also pick it on the map.'))
        .fontFamily(FONT).fontSize(fs(12.5)).fontColor(P().textVar).margin({ top: 10 })
    } else if (this.searched) {
      Text(tr(`${this.results.length} ${plural(this.results.length, 'wynik', 'wyniki', 'wyników')} w Krakowie`,
        `${this.results.length} ${this.results.length === 1 ? 'result' : 'results'} in Kraków`))
        .fontFamily(FONT_B).fontSize(fs(14.5)).fontColor(P().text)
        .width('100%').padding({ top: 16, bottom: 8 })
        .border({ width: { bottom: 1 }, color: P().outlineVar })
      ForEach(this.results, (r: GeocodeResult) => {
        Row({ space: 12 }) {
          Icon({ name: 'pin_outline', iconSize: 20, color: P().text })
          Column({ space: 2 }) {
            Text(r.name).fontFamily(FONT_B).fontSize(fs(15)).fontColor(P().text)
            if (r.address.length > 0) {
              Text(r.address).fontFamily(FONT).fontSize(fs(13)).fontColor(P().textVar)
            }
          }
          .alignItems(HorizontalAlign.Start)
          .layoutWeight(1)
          Icon({ name: 'chevron_right', iconSize: 22, color: P().text })
        }
        .width('100%')
        .padding({ top: 12, bottom: 12 })
        .border({ width: { bottom: 1 }, color: P().outlineVar })
        .focusable(true)
        .accessibilityGroup(true)
        .onClick(() => this.choose(r))
      }, (r: GeocodeResult) => r.id)
      Text(this.isStart() ? tr('Wybierz wynik z listy, żeby ustawić start. Sami niczego nie wybieramy, także gdy wynik jest jeden.',
        'Choose a result from the list to set the start. We never choose for you, even when there is only one result.') :
        tr('Wybierz wynik z listy, żeby ustawić cel. Sami niczego nie wybieramy, także gdy wynik jest jeden.',
          'Choose a result from the list to set the destination. We never choose for you, even when there is only one result.'))
        .fontFamily(FONT).fontSize(fs(12.5)).fontColor(P().textVar).margin({ top: 12 })
    }
    LinkText({ label: tr('Wskaż punkt na mapie', 'Pick a point on the map'),
      action: () => this.nav.replace(AppScreen.PICK, this.target) }).margin({ top: 14 })
  }
}
