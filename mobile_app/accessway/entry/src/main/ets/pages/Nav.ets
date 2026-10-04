export enum AppScreen {
  NEEDS = 'needs',
  MAP = 'map',
  PLAN = 'plan',
  SEARCH = 'search',
  PICK = 'pick',
  ROUTE = 'route',
  FACT = 'fact',
  REPORT = 'report',
  ACCOUNT = 'account',
  PRIVACY = 'privacy',
  ABOUT = 'about',
  MODERATION = 'moderation'
}

/** Przejścia między ekranami, przekazywane ekranom przez powłokę aplikacji. */
export class Nav {
  go: (s: AppScreen, arg: string) => void = () => {
  };
  replace: (s: AppScreen, arg: string) => void = () => {
  };
  back: () => void = () => {
  };
  home: () => void = () => {
  };
  refresh: () => void = () => {
  };
  toast: (m: string) => void = () => {
  };
  previous: () => string = () => '';

  /** Po wyborze punktu wraca do planowania: zdejmuje ekran, jeśli pod nim jest planowanie, inaczej je otwiera. */
  toPlan(): void {
    if (this.previous() === AppScreen.PLAN) {
      this.back();
    } else {
      this.replace(AppScreen.PLAN, '');
    }
  }
}
