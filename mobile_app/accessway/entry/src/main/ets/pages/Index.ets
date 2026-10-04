import { common } from '@kit.AbilityKit';
import { appModel, errorText, PRODUCT_NAME } from '../data/AppModel';
import { tileStore } from '../data/Tiles';
import { getLang, Lang, tr } from '../model/I18n';
import { formatDate } from '../model/Labels';
import { FONT, FONT_B, FONT_TITLE, fs, P, RADIUS, TOUCH } from '../components/Theme';
import { Icon, Segmented } from '../components/Ui';
import { AccountView } from './AccountView';
import { FactView } from './FactView';
import { MapHome } from './MapHome';
import { ModerationView } from './ModerationView';
import { Nav, AppScreen } from './Nav';
import { NeedsView } from './NeedsView';
import { AboutView, PrivacyView } from './InfoPages';
import { PickView } from './PickView';
import { PlanView } from './PlanView';
import { ReportView } from './ReportView';
import { RouteView } from './RouteView';
import { SearchView } from './SearchView';

interface Entry {
  screen: AppScreen;
  arg: string;
}

const MAP_SCREENS: AppScreen[] = [AppScreen.MAP, AppScreen.PLAN, AppScreen.SEARCH, AppScreen.PICK, AppScreen.ROUTE, AppScreen.FACT];

@Entry
@Component
struct Index {
  @State version: number = 0;
  @State stack: Entry[] = [];
  @State menuOpen: boolean = false;
  @State loading: boolean = true;
  private nav: Nav = new Nav();

  aboutToAppear(): void {
    this.nav.go = (s: AppScreen, arg: string) => this.push(s, arg);
    this.nav.replace = (s: AppScreen, arg: string) => this.replaceTop(s, arg);
    this.nav.back = () => this.pop();
    this.nav.home = () => this.reset(AppScreen.MAP);
    this.nav.refresh = () => {
      this.version++;
    };
    this.nav.toast = (m: string) => this.toast(m);
    this.nav.previous = (): string => this.stack.length > 1 ? this.stack[this.stack.length - 2].screen : '';
    setTimeout(() => {
      appModel.init(this.getUIContext().getHostContext() as common.UIAbilityContext);
      this.start();
    }, 60);
  }

  private async start(): Promise<void> {
    await tileStore.init();
    const steps: (() => Promise<void>)[] = [
      () => appModel.refreshInfo(), () => appModel.refreshFacts(), () => appModel.refreshAccount()
    ];
    let failure = '';
    for (const step of steps) {
      try {
        await step();
      } catch (e) {
        failure = failure.length > 0 ? failure : errorText(e as Object);
      }
    }
    if (failure.length > 0) {
      this.toast(failure);
    }
    this.stack = [{ screen: appModel.needsDone ? AppScreen.MAP : AppScreen.NEEDS, arg: '' }];
    this.loading = false;
    this.version++;
  }

  onBackPress(): boolean {
    if (this.menuOpen) {
      this.menuOpen = false;
      this.version++;
      return true;
    }
    if (this.stack.length > 1) {
      this.pop();
      return true;
    }
    if (this.top().screen !== AppScreen.MAP && appModel.needsDone) {
      this.reset(AppScreen.MAP);
      return true;
    }
    return false;
  }

  private toast(msg: string): void {
    try {
      this.getUIContext().getPromptAction().showToast({ message: msg, duration: 2500 });
    } catch (e) {
      return;
    }
  }

  private push(s: AppScreen, arg: string): void {
    const next = this.stack.slice();
    next.push({ screen: s, arg: arg });
    this.stack = next;
    this.menuOpen = false;
    this.version++;
  }

  private replaceTop(s: AppScreen, arg: string): void {
    const next = this.stack.slice();
    next.pop();
    next.push({ screen: s, arg: arg });
    this.stack = next;
    this.version++;
  }

  private pop(): void {
    if (this.stack.length <= 1) {
      this.reset(AppScreen.MAP);
      return;
    }
    const next = this.stack.slice();
    next.pop();
    this.stack = next;
    this.version++;
  }

  private reset(s: AppScreen): void {
    this.stack = [{ screen: s, arg: '' }];
    this.menuOpen = false;
    this.version++;
  }

  private top(): Entry {
    if (this.stack.length === 0) {
      return { screen: AppScreen.MAP, arg: '' };
    }
    return this.stack[this.stack.length - 1];
  }

  private firstRun(): boolean {
    return this.top().screen === AppScreen.NEEDS && !appModel.needsDone;
  }

  build() {
    Stack() {
      if (this.loading) {
        this.splash()
      } else {
        ForEach([this.version], (v: number) => {
          this.shell()
        }, (v: number) => `${v}-${this.stack.length}-${this.top().screen}-${this.top().arg}-${this.menuOpen}`)
      }
    }
    .width('100%')
    .height('100%')
  }

  /** The shell is rebuilt after a data change, because language and data are not component state. */
  @Builder
  shell() {
    Column() {
      this.header()
      Stack({ alignContent: Alignment.Top }) {
        Column() {
          this.screen()
        }
        .width('100%')
        .height('100%')
        if (this.menuOpen) {
          this.menu()
        }
      }
      .layoutWeight(1)
      .width('100%')
      if (!this.firstRun()) {
        this.bottomBar()
      }
    }
    .width('100%')
    .height('100%')
    .backgroundColor(P().card)
  }

  @Builder
  screen() {
    if (!appModel.ready) {
      Text(appModel.loadError.length > 0 ? appModel.loadError : tr('Brak danych mapy', 'No map data'))
        .fontFamily(FONT).fontSize(fs(16)).fontColor(P().barrier).padding(16)
    } else if (this.top().screen === AppScreen.NEEDS) {
      NeedsView({ nav: this.nav, firstRun: !appModel.needsDone, fromRoute: this.top().arg === 'route' })
    } else if (this.top().screen === AppScreen.PLAN) {
      PlanView({ nav: this.nav })
    } else if (this.top().screen === AppScreen.SEARCH) {
      SearchView({ nav: this.nav, target: this.top().arg })
    } else if (this.top().screen === AppScreen.PICK) {
      PickView({ nav: this.nav, target: this.top().arg })
    } else if (this.top().screen === AppScreen.ROUTE) {
      RouteView({ nav: this.nav })
    } else if (this.top().screen === AppScreen.FACT) {
      FactView({ nav: this.nav, factId: this.top().arg })
    } else if (this.top().screen === AppScreen.REPORT) {
      ReportView({ nav: this.nav })
    } else if (this.top().screen === AppScreen.ACCOUNT) {
      AccountView({ nav: this.nav, mode: this.top().arg })
    } else if (this.top().screen === AppScreen.PRIVACY) {
      PrivacyView({ nav: this.nav })
    } else if (this.top().screen === AppScreen.ABOUT) {
      AboutView({ nav: this.nav })
    } else if (this.top().screen === AppScreen.MODERATION) {
      ModerationView({ nav: this.nav })
    } else {
      MapHome({ nav: this.nav })
    }
  }

  @Builder
  header() {
    Row() {
      Text(PRODUCT_NAME).fontFamily(FONT_TITLE).fontSize(fs(18)).fontColor(P().onPrimary)
        .layoutWeight(1).maxLines(1).accessibilityLevel('yes')
      if (this.firstRun()) {
        Button(getLang() === Lang.PL ? 'English' : 'Polski')
          .type(ButtonType.Normal)
          .fontFamily(FONT_B).fontSize(fs(13)).fontColor(P().onPrimary)
          .backgroundColor(Color.Transparent)
          .borderRadius(RADIUS)
          .border({ width: 1.5, color: '#FFFFFF' })
          .height(36)
          .padding({ left: 10, right: 10 })
          .accessibilityText(getLang() === Lang.PL ? 'Switch to English' : 'Przełącz na polski')
          .onClick(() => {
            appModel.setLang(getLang() === Lang.PL ? Lang.EN : Lang.PL);
            this.version++;
          })
      } else {
        Button({ type: ButtonType.Normal }) {
          Icon({ name: this.menuOpen ? 'close_thin' : 'menu', iconSize: 24, color: P().onPrimary })
        }
        .width(TOUCH).height(TOUCH).backgroundColor(Color.Transparent)
        .accessibilityText(this.menuOpen ? tr('Zamknij menu', 'Close the menu') : tr('Menu', 'Menu'))
        .onClick(() => {
          this.menuOpen = !this.menuOpen;
          if (this.menuOpen) {
            appModel.refreshAccount().then(() => {
              this.version++;
            });
          }
          this.version++;
        })
      }
    }
    .width('100%')
    .height(54)
    .padding({ left: 16, right: 6 })
    .backgroundColor(P().primary)
  }

  @Builder
  menuRow(icon: string, title: string, sub: string, action: () => void) {
    Row({ space: 14 }) {
      Icon({ name: icon, iconSize: 22, color: P().text })
      Column({ space: 2 }) {
        Text(title).fontFamily(FONT_B).fontSize(fs(15)).fontColor(P().text)
        if (sub.length > 0) {
          Text(sub).fontFamily(FONT).fontSize(fs(12.5)).fontColor(P().textVar)
        }
      }
      .alignItems(HorizontalAlign.Start)
      .layoutWeight(1)
      Icon({ name: 'chevron_right', iconSize: 22, color: P().text })
    }
    .width('100%')
    .constraintSize({ minHeight: 54 })
    .padding({ top: 8, bottom: 8 })
    .border({ width: { bottom: 1 }, color: P().outlineVar })
    .focusable(true)
    .accessibilityGroup(true)
    .onClick(action)
  }

  /** Menu from mockup V-10: account, language, privacy, data, and moderation for an account with moderator role. */
  @Builder
  menu() {
    Column() {
      Column() {
        this.menuRow('person_outline', tr('Konto', 'Account'), appModel.account !== null ?
          tr(`zalogowano jako ${appModel.accountName()}`, `signed in as ${appModel.accountName()}`) :
          tr('nie zalogowano', 'not signed in'), () => this.push(AppScreen.ACCOUNT, ''))
        Row({ space: 14 }) {
          Icon({ name: 'globe', iconSize: 22, color: P().text })
          Text(tr('Język', 'Language')).fontFamily(FONT_B).fontSize(fs(15)).fontColor(P().text).layoutWeight(1)
          Segmented({
            options: ['Polski', 'English'],
            selected: getLang() === Lang.PL ? 0 : 1,
            onSelect: (i: number) => {
              appModel.setLang(i === 0 ? Lang.PL : Lang.EN);
              this.version++;
            }
          }).width(170)
        }
        .width('100%')
        .height(58)
        .border({ width: { bottom: 1 }, color: P().outlineVar })
        this.menuRow('lock', tr('Informacja o prywatności', 'Privacy information'), '',
          () => this.push(AppScreen.PRIVACY, ''))
        this.menuRow('info_outline', tr('O danych', 'About the data'),
          tr(`OpenStreetMap z dnia ${formatDate(appModel.info().osmDate)}`,
            `OpenStreetMap from ${formatDate(appModel.info().osmDate)}`), () => this.push(AppScreen.ABOUT, ''))
        if (appModel.isModerator()) {
          this.menuRow('shield', tr('Moderacja', 'Moderation'),
            tr('widoczne tylko dla konta z rolą moderatora', 'visible only to a moderator account'),
            () => this.push(AppScreen.MODERATION, ''))
        }
      }
      .width('100%')
      .padding({ left: 16, right: 16, bottom: 4 })
      .backgroundColor(P().card)
      .borderRadius({ bottomLeft: 14, bottomRight: 14 })
      .shadow({ radius: 12, color: '#33000000', offsetY: 4 })
      Column()
        .width('100%')
        .layoutWeight(1)
        .backgroundColor(P().scrim)
        .accessibilityText(tr('Zamknij menu', 'Close the menu'))
        .onClick(() => {
          this.menuOpen = false;
          this.version++;
        })
    }
    .width('100%')
    .height('100%')
  }

  @Builder
  tab(icon: string, label: string, active: boolean, action: () => void) {
    Column({ space: 3 }) {
      Icon({ name: icon, iconSize: 22, color: active ? P().primary : P().textVar })
      Text(label).fontFamily(FONT_B).fontSize(fs(12)).fontColor(active ? P().primary : P().textVar).maxLines(1)
    }
    .layoutWeight(1)
    .height(56)
    .justifyContent(FlexAlign.Center)
    .focusable(true)
    .accessibilityGroup(true)
    .accessibilityText(label + (active ? tr(', wybrane', ', selected') : ''))
    .onClick(action)
  }

  /** Bottom bar from the mockup: Mapa (Map), the yellow Zgłoś (Report) action in the middle, and Potrzeby (Needs). */
  @Builder
  bottomBar() {
    Row({ space: 8 }) {
      this.tab('map_outline', tr('Mapa', 'Map'), MAP_SCREENS.indexOf(this.top().screen) >= 0,
        () => this.reset(AppScreen.MAP))
      Button({ type: ButtonType.Normal }) {
        Row({ space: 8 }) {
          Icon({ name: 'flag_outline', iconSize: 20, color: P().onYellow })
          Text(tr('Zgłoś', 'Report')).fontFamily(FONT_B).fontSize(fs(15)).fontColor(P().onYellow)
        }
      }
      .layoutWeight(1.25)
      .height(48)
      .borderRadius(RADIUS)
      .backgroundColor(P().yellow)
      .border({ width: this.top().screen === AppScreen.REPORT ? 2 : 0, color: P().text })
      .accessibilityText(tr('Zgłoś barierę, udogodnienie albo obszar', 'Report a barrier, an amenity or an area'))
      .onClick(() => this.reset(AppScreen.REPORT))
      this.tab('tune', tr('Potrzeby', 'Needs'), this.top().screen === AppScreen.NEEDS, () => this.reset(AppScreen.NEEDS))
    }
    .width('100%')
    .padding({ left: 12, right: 12, top: 6, bottom: 6 })
    .backgroundColor(P().card)
    .border({ width: { top: 1 }, color: P().outlineVar })
  }

  @Builder
  splash() {
    Column({ space: 16 }) {
      Text(PRODUCT_NAME).fontFamily(FONT_TITLE).fontSize(22).fontColor('#FFFFFF')
      LoadingProgress().width(44).height(44).color('#FFD400')
    }
    .width('100%')
    .height('100%')
    .justifyContent(FlexAlign.Center)
    .backgroundColor('#12306B')
  }
}
