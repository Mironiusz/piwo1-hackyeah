import { common } from '@kit.AbilityKit';
import { appModel, Endpoint, errorText } from '../data/AppModel';
import { currentPosition } from '../data/Location';
import { tr } from '../model/I18n';
import { streetLabel } from '../model/Labels';
import { MapCanvas, MapMode } from '../components/MapCanvas';
import { FONT, fs, P } from '../components/Theme';
import { Btn, BtnKind, BoxKind, MessageBox, SheetBox, SheetTitle } from '../components/Ui';
import { Nav } from './Nav';

/** Wskazanie startu albo celu na mapie: krzyżyk na środku, mapę przesuwa się palcem albo strzałkami. */
@Component
export struct PickView {
  nav: Nav = new Nav();
  target: string = 'dest';
  @State error: string = '';

  private async locate(): Promise<void> {
    try {
      const p = await currentPosition(this.getUIContext().getHostContext() as common.UIAbilityContext);
      appModel.mapLat = p.lat;
      appModel.mapLon = p.lon;
      this.nav.refresh();
    } catch (e) {
      this.error = errorText(e as Object);
    }
  }

  private async setPoint(): Promise<void> {
    const lat = appModel.mapLat;
    const lon = appModel.mapLon;
    const street = await appModel.repo.geocoding.streetAt(lat, lon);
    const e: Endpoint = {
      lat: lat,
      lon: lon,
      label: street.length > 0 ? tr(`Punkt przy ${streetLabel(street)}`, `Point at ${streetLabel(street)}`) :
        tr('Punkt wskazany na mapie', 'Point picked on the map')
    };
    if (this.target === 'start') {
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
        MapCanvas({ mapHeight: 370, mode: MapMode.PICK, showLocate: true, onLocate: () => {
          this.locate();
        } })
        SheetBox() {
          SheetTitle({
            title: this.target === 'start' ? tr('Wskaż start na mapie', 'Pick the start on the map') :
              tr('Wskaż cel na mapie', 'Pick the destination on the map'),
            onClose: () => this.nav.back()
          })
          Text(tr('Przesuń mapę, aż znacznik na środku wskaże miejsce. Na klawiaturze przesuwasz mapę strzałkami.',
            'Move the map until the marker in the middle points at the place. With a keyboard, move the map with the arrow keys.'))
            .fontFamily(FONT).fontSize(fs(13.5)).fontColor(P().textVar).margin({ top: 6 })
          if (this.error.length > 0) {
            MessageBox({ text: this.error, kind: BoxKind.ERROR }).margin({ top: 10 })
          }
          Row({ space: 10 }) {
            Btn({ label: tr('Wróć', 'Back'), kind: BtnKind.OUTLINE, action: () => this.nav.back() }).layoutWeight(1)
            Btn({ label: tr('Ustaw ten punkt', 'Set this point'), action: () => {
              this.setPoint();
            } }).layoutWeight(1)
          }
          .width('100%')
          .margin({ top: 16 })
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
}
