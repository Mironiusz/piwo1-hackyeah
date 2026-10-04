import { appModel } from '../data/AppModel';
import { copyNeeds, Needs, Preset, presetIcon, presetLabel, presetNeeds, PRESETS, toggleKind } from '../domain/Needs';
import { tr } from '../model/I18n';
import { kindLabel } from '../model/Labels';
import { AMENITY_KINDS, BARRIER_KINDS, FactCategory, FactKind } from '../model/Types';
import { KindIcon } from '../components/Glyphs';
import { FONT, FONT_B, fs, P, RADIUS } from '../components/Theme';
import { Btn, BtnKind, Icon, PageTitle } from '../components/Ui';
import { Nav } from './Nav';

/** V-2: needs. On first open with the Pomiń (Skip) and Gotowe (Done) buttons, later as the Potrzeby (Needs) tab. */
@Component
export struct NeedsView {
  nav: Nav = new Nav();
  firstRun: boolean = false;
  fromRoute: boolean = false;
  @State draft: Needs = copyNeeds(appModel.needs);

  private apply(p: Preset): void {
    this.draft = presetNeeds(p);
  }

  private async finish(save: boolean): Promise<void> {
    if (save) {
      appModel.setNeeds(this.draft);
    }
    appModel.needsDone = true;
    appModel.savePrefs();
    if (appModel.plan !== null || appModel.planError.length > 0) {
      await appModel.computeRoute();
    }
    if (this.fromRoute) {
      this.nav.back();
    } else {
      this.nav.home();
    }
  }

  build() {
    Scroll() {
      Column({ space: 0 }) {
        PageTitle({
          title: tr('Twoje potrzeby', 'Your needs'),
          intro: tr('Zaznacz, czego unikasz i czego potrzebujesz po drodze. Nie pytamy o niepełnosprawność. Te ustawienia zostają tylko na tym urządzeniu.',
            'Mark what you avoid and what you need on the way. We do not ask about disability. These settings stay only on this device.')
        })
        Text(tr('Zacznij od gotowego zestawu', 'Start from a ready set'))
          .fontFamily(FONT_B).fontSize(fs(13.5)).fontColor(P().text).margin({ top: 18, bottom: 8 })
          .width('100%')
        Column({ space: 8 }) {
          ForEach(PRESETS, (p: Preset) => {
            Button({ type: ButtonType.Normal }) {
              Row({ space: 12 }) {
                Icon({ name: presetIcon(p), iconSize: 20, color: P().primary })
                Text(presetLabel(p)).fontFamily(FONT_B).fontSize(fs(14.5)).fontColor(P().primary)
              }
              .width('100%')
              .padding({ left: 14, right: 14 })
            }
            .width('100%')
            .height(44)
            .borderRadius(RADIUS)
            .backgroundColor(P().card)
            .border({ width: 1.5, color: P().primary })
            .onClick(() => this.apply(p))
          }, (p: Preset) => p)
        }
        this.groupTitle(tr('Unikam', 'I avoid'))
        ForEach(BARRIER_KINDS, (k: FactKind) => {
          this.checkRow(k, true)
        }, (k: FactKind) => `a-${k}-${this.draft.avoid.indexOf(k) >= 0}`)
        this.groupTitle(tr('Potrzebuję', 'I need'))
        ForEach(AMENITY_KINDS, (k: FactKind) => {
          this.checkRow(k, false)
        }, (k: FactKind) => `n-${k}-${this.draft.need.indexOf(k) >= 0}`)
        Row({ space: 10 }) {
          if (this.firstRun) {
            Btn({ label: tr('Pomiń', 'Skip'), kind: BtnKind.OUTLINE, action: () => {
              this.finish(false);
            } }).layoutWeight(1)
          }
          Btn({ label: tr('Gotowe', 'Done'), kind: BtnKind.PRIMARY, action: () => {
            this.finish(true);
          } }).layoutWeight(1)
        }
        .width('100%')
        .margin({ top: 16 })
        Text(tr('Bez żadnej zaznaczonej bariery pokażemy trasę, ale nie ocenimy jej odcinków.',
          'With no barrier marked we still show a route, but we do not rate its segments.'))
          .fontFamily(FONT).fontSize(fs(12.5)).fontColor(P().textVar).margin({ top: 10 }).width('100%')
      }
      .width('100%')
      .padding({ left: 16, right: 16, top: 18, bottom: 28 })
      .alignItems(HorizontalAlign.Start)
    }
    .width('100%')
    .height('100%')
    .align(Alignment.Top)
    .edgeEffect(EdgeEffect.None)
    .backgroundColor(P().card)
  }

  @Builder
  groupTitle(text: string) {
    Text(text).fontFamily(FONT_B).fontSize(fs(14)).fontColor(P().text)
      .width('100%')
      .padding({ top: 20, bottom: 8 })
      .border({ width: { bottom: 1 }, color: P().outlineVar })
      .accessibilityLevel('yes')
  }

  @Builder
  checkRow(k: FactKind, avoid: boolean) {
    Row({ space: 12 }) {
      Checkbox({ name: k, group: avoid ? 'avoid' : 'need' })
        .select(avoid ? this.draft.avoid.indexOf(k) >= 0 : this.draft.need.indexOf(k) >= 0)
        .selectedColor(P().primary)
        .shape(CheckBoxShape.ROUNDED_SQUARE)
        .width(22)
        .height(22)
        .accessibilityText(kindLabel(k))
        .onChange((v: boolean) => {
          const on = avoid ? this.draft.avoid.indexOf(k) >= 0 : this.draft.need.indexOf(k) >= 0;
          if (v !== on) {
            this.toggle(k, avoid);
          }
        })
      KindIcon({ kind: k, category: avoid ? FactCategory.BARRIER : FactCategory.AMENITY, iconSize: 18, color: P().text })
      Text(kindLabel(k)).fontFamily(FONT).fontSize(fs(15)).fontColor(P().text).layoutWeight(1)
    }
    .width('100%')
    .height(48)
    .border({ width: { bottom: 1 }, color: P().outlineVar })
    .onClick(() => this.toggle(k, avoid))
  }

  private toggle(k: FactKind, avoid: boolean): void {
    const n = copyNeeds(this.draft);
    if (avoid) {
      n.avoid = toggleKind(n.avoid, k);
    } else {
      n.need = toggleKind(n.need, k);
    }
    this.draft = n;
  }
}
