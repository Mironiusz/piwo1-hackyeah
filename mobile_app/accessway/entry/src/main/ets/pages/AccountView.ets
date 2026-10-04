import { appModel, errorText } from '../data/AppModel';
import { ErrorCode, RepoError } from '../data/Repository';
import { tr } from '../model/I18n';
import { FONT, FONT_B, fs, P, RADIUS } from '../components/Theme';
import { BackLink, Btn, BtnKind, BoxKind, Bullet, LinkText, MessageBox, PageBox, PageTitle, SubTitle } from '../components/Ui';
import { Nav, AppScreen } from './Nav';

/** V-11: account with a nickname and password, no email address; sign-in, sign-up, sign-out and deletion. */
@Component
export struct AccountView {
  nav: Nav = new Nav();
  mode: string = '';
  @State pseudonym: string = '';
  @State password: string = '';
  @State error: string = '';
  @State pseudonymError: string = '';
  @State busy: boolean = false;

  private async login(): Promise<void> {
    this.busy = true;
    this.error = '';
    try {
      await appModel.repo.accounts.login(this.pseudonym, this.password);
      await appModel.refreshAccount();
      this.nav.replace(AppScreen.ACCOUNT, '');
    } catch (e) {
      this.error = errorText(e as Object);
    }
    this.busy = false;
  }

  private async signup(): Promise<void> {
    this.busy = true;
    this.error = '';
    this.pseudonymError = '';
    try {
      await appModel.repo.accounts.signup(this.pseudonym, this.password);
      await appModel.refreshAccount();
      this.nav.replace(AppScreen.ACCOUNT, '');
    } catch (e) {
      if (e instanceof RepoError && ((e as RepoError).code === ErrorCode.TAKEN ||
        (e as RepoError).code === ErrorCode.INVALID_PSEUDONYM)) {
        this.pseudonymError = (e as RepoError).message;
      } else {
        this.error = errorText(e as Object);
      }
    }
    this.busy = false;
  }

  private async logout(): Promise<void> {
    await appModel.repo.accounts.logout();
    await appModel.refreshAccount();
    this.nav.refresh();
  }

  private async remove(): Promise<void> {
    this.busy = true;
    try {
      await appModel.repo.accounts.deleteAccount();
      await appModel.refreshAccount();
      this.nav.toast(tr('Konto usunięte', 'Account deleted'));
      this.nav.replace(AppScreen.ACCOUNT, '');
    } catch (e) {
      this.error = errorText(e as Object);
    }
    this.busy = false;
  }

  build() {
    PageBox() {
      BackLink({ action: () => this.nav.back() })
      if (this.mode === 'delete' && appModel.account !== null) {
        this.deleteView()
      } else if (this.mode === 'signup') {
        this.signupView()
      } else if (appModel.account !== null) {
        this.loggedView()
      } else {
        this.loginView()
      }
    }
  }

  @Builder
  field(label: string, value: string, secret: boolean, hint: string, err: string, onChange: (v: string) => void) {
    Text(label).fontFamily(FONT_B).fontSize(fs(13)).fontColor(P().text).margin({ top: 14, bottom: 6 })
    TextInput({ text: value })
      .type(secret ? InputType.Password : InputType.Normal)
      .showPasswordIcon(false)
      .fontFamily(FONT).fontSize(fs(15))
      .width('100%').height(46)
      .borderRadius(RADIUS).backgroundColor(P().card)
      .border({ width: err.length > 0 ? 1.5 : 1, color: err.length > 0 ? P().barrier : P().textVar })
      .accessibilityText(label)
      .onChange(onChange)
    if (hint.length > 0) {
      Text(hint).fontFamily(FONT).fontSize(fs(12)).fontColor(P().textVar).margin({ top: 6 })
    }
    if (err.length > 0) {
      Text(err).fontFamily(FONT_B).fontSize(fs(12.5)).fontColor(P().barrier).margin({ top: 4 })
    }
  }

  @Builder
  loginView() {
    PageTitle({
      title: tr('Konto', 'Account'),
      intro: tr('Konto to pseudonim i hasło, bez adresu e-mail. Zgłaszać i głosować możesz też bez konta.',
        'An account is a nickname and a password, without an e-mail address. You can report and vote without an account too.')
    })
    this.field(tr('Pseudonim', 'Nickname'), this.pseudonym, false, '', '', (v: string) => {
      this.pseudonym = v;
    })
    this.field(tr('Hasło', 'Password'), this.password, true, '', '', (v: string) => {
      this.password = v;
    })
    if (this.error.length > 0) {
      MessageBox({ text: this.error, kind: BoxKind.ERROR }).margin({ top: 14 })
    }
    Btn({ label: tr('Zaloguj się', 'Sign in'), enabledState: !this.busy && this.pseudonym.length > 0 &&
      this.password.length > 0, action: () => {
      this.login();
    } }).margin({ top: 16 })
    Text(tr('Nie masz konta?', 'No account yet?')).fontFamily(FONT).fontSize(fs(14)).fontColor(P().text)
      .margin({ top: 22, bottom: 8 })
    Btn({ label: tr('Załóż konto', 'Create an account'), kind: BtnKind.OUTLINE,
      action: () => this.nav.replace(AppScreen.ACCOUNT, 'signup') })
  }

  @Builder
  signupView() {
    PageTitle({
      title: tr('Załóż konto', 'Create an account'),
      intro: tr('Wystarczy pseudonim i hasło. Nie pytamy o adres e-mail ani o niepełnosprawność.',
        'A nickname and a password are enough. We do not ask for an e-mail address or about disability.')
    })
    this.field(tr('Pseudonim', 'Nickname'), this.pseudonym, false,
      tr('3 do 30 znaków: litery, cyfry, podkreślenie i myślnik.', '3 to 30 characters: letters, digits, underscore and hyphen.'),
      this.pseudonymError, (v: string) => {
        this.pseudonym = v;
        this.pseudonymError = '';
      })
    this.field(tr('Hasło', 'Password'), this.password, true,
      tr('Co najmniej 5 znaków. Mogą być spacje.', 'At least 5 characters. Spaces are allowed.'), '', (v: string) => {
        this.password = v;
      })
    MessageBox({
      lead: tr('Hasła nie da się odzyskać.', 'The password cannot be recovered.'),
      text: tr('Nie mamy Twojego adresu e-mail, więc jeśli zapomnisz hasła, stracisz dostęp do konta na stałe.',
        'We do not have your e-mail address, so if you forget the password you lose the account for good.'),
      kind: BoxKind.ERROR
    }).margin({ top: 16 })
    if (this.error.length > 0) {
      MessageBox({ text: this.error, kind: BoxKind.ERROR }).margin({ top: 10 })
    }
    Btn({ label: tr('Załóż konto', 'Create an account'), enabledState: !this.busy, action: () => {
      this.signup();
    } }).margin({ top: 16 })
    LinkText({ label: tr('Mam już konto', 'I already have an account'),
      action: () => this.nav.replace(AppScreen.ACCOUNT, '') }).margin({ top: 14 })
  }

  @Builder
  loggedView() {
    PageTitle({ title: tr('Konto', 'Account') })
    Row({ space: 14 }) {
      Text(tr('Zalogowano jako', 'Signed in as')).fontFamily(FONT).fontSize(fs(14)).fontColor(P().textVar)
      Text(appModel.accountName()).fontFamily(FONT_B).fontSize(fs(14.5))
        .fontColor(P().text)
    }
    .margin({ top: 10 })
    MessageBox({
      text: tr('Zostajesz zalogowany na tym urządzeniu przez 24 godziny od ostatniego użycia aplikacji, także po jej zamknięciu.',
        'You stay signed in on this device for 24 hours after you last used the app, also after closing it.'),
      kind: BoxKind.INFO
    }).margin({ top: 14 })
    MessageBox({
      text: tr('Twoje potrzeby nie są częścią konta. Zostają tylko na tym urządzeniu.',
        'Your needs are not part of the account. They stay only on this device.'),
      kind: BoxKind.INFO
    }).margin({ top: 8 })
    Btn({ label: tr('Wyloguj się', 'Sign out'), kind: BtnKind.OUTLINE, action: () => {
      this.logout();
    } }).margin({ top: 16 })
    SubTitle({ text: tr('Usunięcie konta', 'Deleting the account') }).margin({ top: 26 })
    Text(tr('Usuniemy konto i pseudonim. Twoje zgłoszenia i głosy zostaną, odłączone od Ciebie.',
      'We delete the account and the nickname. Your reports and votes stay, detached from you.'))
      .fontFamily(FONT).fontSize(fs(14)).fontColor(P().text).margin({ top: 6 })
    LinkText({ label: tr('Usuń konto', 'Delete the account'), danger: true,
      action: () => this.nav.replace(AppScreen.ACCOUNT, 'delete') }).margin({ top: 10 })
  }

  @Builder
  deleteView() {
    PageTitle({ title: tr(`Usunąć konto ${appModel.accountName()}?`,
      `Delete the account ${appModel.accountName()}?`) })
    SubTitle({ text: tr('Co zniknie', 'What goes away') })
    Column({ space: 8 }) {
      Bullet({ text: tr('Konto i możliwość logowania.', 'The account and signing in.') })
      Bullet({ text: tr(`Pseudonim ${appModel.accountName()}. Ktoś inny będzie mógł go potem zająć.`,
        `The nickname ${appModel.accountName()}. Someone else can take it later.`) })
    }
    .margin({ top: 8 })
    SubTitle({ text: tr('Co zostanie', 'What stays') })
    Column({ space: 8 }) {
      Bullet({ text: tr('Twoje zgłoszenia i głosy, odłączone od Ciebie. Nadal liczą się do statusów.',
        'Your reports and votes, detached from you. They still count towards the statuses.') })
      Bullet({ text: tr('Twoje potrzeby na tym urządzeniu, bo nie są częścią konta.',
        'Your needs on this device, because they are not part of the account.') })
    }
    .margin({ top: 8 })
    MessageBox({ text: tr('Tego nie da się cofnąć.', 'This cannot be undone.'), kind: BoxKind.ERROR }).margin({ top: 16 })
    if (this.error.length > 0) {
      MessageBox({ text: this.error, kind: BoxKind.ERROR }).margin({ top: 10 })
    }
    Row({ space: 10 }) {
      Btn({ label: tr('Anuluj', 'Cancel'), kind: BtnKind.OUTLINE, action: () => this.nav.replace(AppScreen.ACCOUNT, '') })
        .layoutWeight(1)
      Btn({ label: tr('Usuń konto', 'Delete the account'), kind: BtnKind.DANGER, enabledState: !this.busy, action: () => {
        this.remove();
      } }).layoutWeight(1)
    }
    .width('100%')
    .margin({ top: 14 })
  }
}
