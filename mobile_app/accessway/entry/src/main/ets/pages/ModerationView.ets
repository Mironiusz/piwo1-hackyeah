import { appModel, errorText } from '../data/AppModel';
import { tr } from '../model/I18n';
import { factTitle, formatDate, streetLabel } from '../model/Labels';
import { Fact } from '../model/Types';
import { FONT, FONT_B, fs, P, RADIUS } from '../components/Theme';
import {
  BackLink,
  Btn,
  BtnKind,
  BoxKind,
  GroupHeader,
  MessageBox,
  PageBox,
  PageTitle,
  SampleChip,
  StatusLine
} from '../components/Ui';
import { Nav, AppScreen } from './Nav';

/** V-14: moderation for an account with the moderator role. It hides who added the content and who flagged it. */
@Component
export struct ModerationView {
  nav: Nav = new Nav();
  @State flagged: Fact[] = [];
  @State hidden: Fact[] = [];
  @State error: string = '';
  @State loaded: boolean = false;

  aboutToAppear(): void {
    this.load();
  }

  private async load(): Promise<void> {
    try {
      this.flagged = await appModel.repo.moderation.flagged();
      this.hidden = await appModel.repo.moderation.hiddenFacts();
      this.error = '';
    } catch (e) {
      this.error = errorText(e as Object);
    }
    this.loaded = true;
  }

  private async hide(id: string): Promise<void> {
    try {
      await appModel.repo.moderation.hide(id);
      await appModel.refreshFacts();
      if (appModel.plan !== null) {
        await appModel.computeRoute();
      }
      await this.load();
    } catch (e) {
      this.error = errorText(e as Object);
    }
  }

  private async restore(id: string): Promise<void> {
    try {
      await appModel.repo.moderation.restore(id);
      await appModel.refreshFacts();
      if (appModel.plan !== null) {
        await appModel.computeRoute();
      }
      await this.load();
    } catch (e) {
      this.error = errorText(e as Object);
    }
  }

  private showOnMap(f: Fact): void {
    appModel.fitTo(f.lat, f.lon, 120);
    this.nav.go(AppScreen.FACT, f.id);
  }

  build() {
    PageBox() {
      BackLink({ action: () => this.nav.back() })
      PageTitle({
        title: tr('Moderacja', 'Moderation'),
        intro: tr('Treści zgłoszone przez użytkowników. Nie widać tu, kto dodał treść ani kto ją zgłosił.',
          'Content flagged by users. You cannot see here who added the content or who flagged it.')
      })
      if (this.error.length > 0) {
        MessageBox({ text: this.error, kind: BoxKind.ERROR }).margin({ top: 12 })
      }
      GroupHeader({ title: tr('Zgłoszone do moderacji', 'Flagged for moderation'), count: `${this.flagged.length}` })
      if (this.loaded && this.flagged.length === 0) {
        MessageBox({ text: tr('Nie ma zgłoszeń do moderacji.', 'Nothing is flagged.'), kind: BoxKind.INFO })
          .margin({ top: 10 })
      }
      ForEach(this.flagged, (f: Fact) => {
        this.card(f, false)
      }, (f: Fact) => `f-${f.id}`)
      Text(tr('Zgłoszenia do moderacji nie da się odrzucić. Treść, której nie ukryjesz, zostaje na tej liście.',
        'A flag cannot be dismissed. Content you do not hide stays on this list.'))
        .fontFamily(FONT).fontSize(fs(12.5)).fontColor(P().textVar).margin({ top: 10 })
      GroupHeader({ title: tr('Ukryte', 'Hidden'), count: `${this.hidden.length}` })
      ForEach(this.hidden, (f: Fact) => {
        this.card(f, true)
      }, (f: Fact) => `h-${f.id}`)
      Text(tr('Ukryta treść znika z map, list i tras, nie bierze udziału w sprawdzaniu duplikatów i nie można na nią głosować. Po przywróceniu wraca z głosami, które ma.',
        'Hidden content disappears from maps, lists and routes, takes no part in duplicate checks and cannot be voted on. When restored, it comes back with the votes it has.'))
        .fontFamily(FONT).fontSize(fs(12.5)).fontColor(P().textVar).margin({ top: 10 })
    }
  }

  @Builder
  card(f: Fact, isHidden: boolean) {
    Column({ space: 4 }) {
      Text(factTitle(f.kind, f.category, f.stepCount, f.radiusM)).fontFamily(FONT_B).fontSize(fs(15)).fontColor(P().text)
      if (f.street.length > 0) {
        Text(streetLabel(f.street)).fontFamily(FONT).fontSize(fs(13)).fontColor(P().textVar)
      }
      if (f.description.length > 0) {
        Text(tr(`Opis: ${f.description}`, `Description: ${f.description}`)).fontFamily(FONT).fontSize(fs(13.5))
          .fontColor(P().text).margin({ top: 4 })
      }
      if (isHidden) {
        Row({ space: 8 }) {
          Text(tr(`zgłoszenie, ${formatDate(f.date)}`, `report, ${formatDate(f.date)}`)).fontFamily(FONT)
            .fontSize(fs(12.5)).fontColor(P().textVar)
          Text(tr('ukryte dla wszystkich', 'hidden for everyone')).fontFamily(FONT_B).fontSize(fs(11.5))
            .fontColor(P().text).padding({ left: 7, right: 7, top: 3, bottom: 3 }).borderRadius(4)
            .backgroundColor(P().chipBg).border({ width: 1, color: P().outlineVar })
        }
        .margin({ top: 4 })
        Btn({ label: tr('Przywróć', 'Restore'), kind: BtnKind.OUTLINE, action: () => {
          this.restore(f.id);
        } }).margin({ top: 8 })
      } else {
        StatusLine({ fact: f }).margin({ top: 4 })
        Row({ space: 10 }) {
          Btn({ label: tr('Pokaż na mapie', 'Show on the map'), kind: BtnKind.OUTLINE, action: () => this.showOnMap(f) })
            .layoutWeight(1)
          Btn({ label: tr('Ukryj', 'Hide'), action: () => {
            this.hide(f.id);
          } }).layoutWeight(1)
        }
        .width('100%')
        .margin({ top: 8 })
      }
    }
    .width('100%')
    .alignItems(HorizontalAlign.Start)
    .padding(12)
    .margin({ top: 10 })
    .borderRadius(RADIUS)
    .border({ width: 1, color: P().outlineVar })
  }
}
