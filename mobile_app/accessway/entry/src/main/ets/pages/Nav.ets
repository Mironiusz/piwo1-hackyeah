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

/** Transitions between screens, passed to the screens by the app shell. */
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

  /** After a point is picked, returns to planning: pops the screen if planning is below it, otherwise opens it. */
  toPlan(): void {
    if (this.previous() === AppScreen.PLAN) {
      this.back();
    } else {
      this.replace(AppScreen.PLAN, '');
    }
  }
}
