import { common } from '@kit.AbilityKit';
import { appModel, Endpoint, errorText } from '../data/AppModel';
import { currentPosition } from '../data/Location';
import { tr } from '../model/I18n';
import { countAmenities, countBarriers } from '../model/Labels';
import { LatLon } from '../model/Types';
import { MapCanvas } from '../components/MapCanvas';
import { FONT, FONT_B, FONT_TITLE, fs, P } from '../components/Theme';
import { Btn, BtnKind, BoxKind, LinkText, MessageBox, SheetBox } from '../components/Ui';
import { Nav, AppScreen } from './Nav';

/** V-4: route planning. Start and destination from search, map or location; routing errors shown without guessing. */
@Component
export struct PlanView {
  nav: Nav = new Nav();
  @State editStart: boolean = appModel.start === null || appModel.plan === null;
  @State editDest: boolean = appModel.dest === null || appModel.plan === null;
  @State busy: boolean = false;
  @State error: string = appModel.planError;
  @State locError: string = '';

  aboutToAppear(): void {
    const pts: LatLon[] = [];
    if (appModel.start !== null) {
      pts.push({ lat: appModel.start.lat, lon: appModel.start.lon });
    }
    if (appModel.dest !== null) {
      pts.push({ lat: appModel.dest.lat, lon: appModel.dest.lon });
    }
    if (pts.length === 2) {
      appModel.fitBox = [Math.min(pts[0].lat, pts[1].lat), Math.max(pts[0].lat, pts[1].lat),
        Math.min(pts[0].lon, pts[1].lon), Math.max(pts[0].lon, pts[1].lon)];
    } else if (pts.length === 1) {
      appModel.fitTo(pts[0].lat, pts[0].lon, 250);
    }
  }

  private async locate(): Promise<void> {
    this.locError = '';
    try {
      const ctx = this.getUIContext().getHostContext() as common.UIAbilityContext;
      const p = await currentPosition(ctx);
      const e: Endpoint = { lat: p.lat, lon: p.lon, label: tr('Moja lokalizacja', 'My location') };
      appModel.start = e;
      this.editStart = false;
      this.nav.refresh();
    } catch (e) {
      this.locError = errorText(e as Object);
    }
  }

  private async compute(): Promise<void> {
    this.busy = true;
    appModel.avoidFactIds = [];
    const ok = await appModel.computeRoute();
    this.busy = false;
    if (ok) {
      this.nav.replace(AppScreen.ROUTE, '');
    } else {
      this.error = appModel.planError;
    }
  }

  build() {
    Scroll() {
      Column() {
        MapCanvas({ mapHeight: 250, showA: true, showB: true })
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
    Text(tr('Zaplanuj trasę', 'Plan a route')).fontFamily(FONT_TITLE).fontSize(fs(19)).fontColor(P().text)
      .margin({ top: 4, bottom: 6 }).accessibilityLevel('yes')
    this.endpoint('A', tr('Start', 'Start'), appModel.start, this.editStart, true)
    Divider().color(P().outlineVar).margin({ top: 4 })
    this.endpoint('B', tr('Cel', 'Destination'), appModel.dest, this.editDest, false)
    if (this.locError.length > 0) {
      MessageBox({ text: this.locError, kind: BoxKind.ERROR }).margin({ top: 10 })
    }
    if (this.error.length > 0) {
      MessageBox({
        lead: tr('Nie możemy teraz wyznaczyć trasy.', 'We cannot plan the route right now.'),
        text: this.error,
        kind: BoxKind.ERROR
      }).margin({ top: 12 })
      Btn({ label: tr('Spróbuj ponownie', 'Try again'), enabledState: !this.busy, action: () => {
        this.compute();
      } }).margin({ top: 12 })
    } else {
      Text() {
        if (appModel.needs.avoid.length > 0) {
          Span(tr(`Trasa dla Twoich potrzeb: ${countBarriers(appModel.needs.avoid.length)}, ${countAmenities(appModel.needs.need.length)}. `,
            `Route for your needs: ${countBarriers(appModel.needs.avoid.length)}, ${countAmenities(appModel.needs.need.length)}. `))
        } else {
          Span(tr('Twoje potrzeby nie mają żadnej bariery, więc nie ocenimy odcinków trasy. ',
            'Your needs have no barrier, so we will not rate the route segments. '))
        }
        Span(tr('Zmień potrzeby', 'Change needs'))
          .fontFamily(FONT_B)
          .fontColor(P().primary)
          .decoration({ type: TextDecorationType.Underline, color: P().primary })
          .onClick(() => this.nav.go(AppScreen.NEEDS, 'route'))
      }
      .fontFamily(FONT).fontSize(fs(13.5)).fontColor(P().text).lineHeight(fs(19))
      .width('100%')
      .padding({ left: 14, right: 14, top: 11, bottom: 11 })
      .borderRadius(6)
      .border({ width: 1, color: P().outlineVar })
      .margin({ top: 14 })
      Btn({
        label: this.busy ? tr('Wyznaczamy trasę', 'Planning the route') : tr('Wyznacz trasę', 'Plan the route'),
        enabledState: appModel.start !== null && appModel.dest !== null && !this.busy,
        action: () => {
          this.compute();
        }
      }).margin({ top: 14 })
    }
  }

  @Builder
  endpoint(letter: string, label: string, e: Endpoint | null, editing: boolean, isStart: boolean) {
    Column({ space: 10 }) {
      Row({ space: 12 }) {
        Text(letter).fontFamily(FONT_B).fontSize(fs(12)).fontColor(P().text)
          .width(24).height(24).borderRadius(12).textAlign(TextAlign.Center)
          .border({ width: 2, color: P().text })
        Column({ space: 1 }) {
          Text(label).fontFamily(FONT).fontSize(fs(12.5)).fontColor(P().textVar)
          Text(e !== null ? e.label : tr('Nie ustawiono', 'Not set'))
            .fontFamily(FONT_B).fontSize(fs(15)).fontColor(e !== null ? P().text : P().textVar)
        }
        .alignItems(HorizontalAlign.Start)
        .layoutWeight(1)
        if (e !== null) {
          LinkText({ label: tr('Zmień', 'Change'), action: () => {
            if (isStart) {
              this.editStart = !this.editStart;
            } else {
              this.editDest = !this.editDest;
            }
          } })
        }
      }
      .width('100%')
      .accessibilityGroup(false)
      if (editing || e === null) {
        Row({ space: 8 }) {
          if (isStart) {
            Btn({ label: tr('Moja lokalizacja', 'My location'), icon: 'crosshair', kind: BtnKind.OUTLINE, small: true,
              action: () => {
                this.locate();
              } })
          }
          Btn({ label: tr('Adres', 'Address'), kind: BtnKind.OUTLINE, small: true,
            action: () => this.nav.go(AppScreen.SEARCH, isStart ? 'start' : 'dest') })
          Btn({ label: tr('Punkt na mapie', 'Point on the map'), kind: BtnKind.OUTLINE, small: true,
            action: () => this.nav.go(AppScreen.PICK, isStart ? 'start' : 'dest') })
        }
        .margin({ left: 36 })
      }
    }
    .width('100%')
    .padding({ top: 10, bottom: 10 })
  }
}
