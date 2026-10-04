import { AbilityConstant, ConfigurationConstant, UIAbility, Want } from '@kit.AbilityKit';
import { hilog } from '@kit.PerformanceAnalysisKit';
import { window } from '@kit.ArkUI';

const DOMAIN = 0x0A11;
const TAG = 'AccessWay';

export default class EntryAbility extends UIAbility {
  onCreate(want: Want, launchParam: AbilityConstant.LaunchParam): void {
    try {
      this.context.getApplicationContext().setColorMode(ConfigurationConstant.ColorMode.COLOR_MODE_LIGHT);
    } catch (err) {
      hilog.error(DOMAIN, TAG, 'setColorMode failed: %{public}s', JSON.stringify(err));
    }
  }

  onWindowStageCreate(windowStage: window.WindowStage): void {
    windowStage.loadContent('pages/Index', (err) => {
      if (err.code) {
        hilog.error(DOMAIN, TAG, 'loadContent failed: %{public}s', JSON.stringify(err));
        return;
      }
      try {
        const font = windowStage.getMainWindowSync().getUIContext().getFont();
        font.registerFont({ familyName: 'BarlowSC', familySrc: $rawfile('fonts/BarlowSemiCondensed-Regular.ttf') });
        font.registerFont({ familyName: 'BarlowSCSemi', familySrc: $rawfile('fonts/BarlowSemiCondensed-SemiBold.ttf') });
        font.registerFont({ familyName: 'BarlowNum', familySrc: $rawfile('fonts/BarlowCondensed-Bold.ttf') });
        font.registerFont({ familyName: 'BarlowSCBold', familySrc: $rawfile('fonts/BarlowSemiCondensed-Bold.ttf') });
      } catch (e) {
        hilog.warn(DOMAIN, TAG, 'registerFont failed: %{public}s', JSON.stringify(e));
      }
    });
  }
}
