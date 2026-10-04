import { abilityAccessCtrl, common, Permissions } from '@kit.AbilityKit';
import { geoLocationManager } from '@kit.LocationKit';
import { tr } from '../model/I18n';
import { LatLon } from '../model/Types';

const PERMS: Permissions[] = ['ohos.permission.APPROXIMATELY_LOCATION', 'ohos.permission.LOCATION'];

/**
 * Current device position, only when the person asks for it. The position is used for one route or to move the map
 * and is not saved. No permission or no signal ends in an error with a message in the current language.
 */
export async function currentPosition(ctx: common.UIAbilityContext): Promise<LatLon> {
  const atManager = abilityAccessCtrl.createAtManager();
  const res = await atManager.requestPermissionsFromUser(ctx, PERMS);
  let granted = false;
  for (const r of res.authResults) {
    granted = granted || r === 0;
  }
  if (!granted) {
    throw new Error(tr('Bez zgody na lokalizację nie wiemy, gdzie jesteś. Wpisz adres albo wskaż punkt na mapie.',
      'Without location permission we do not know where you are. Type an address or pick a point on the map.'));
  }
  try {
    const loc = await geoLocationManager.getCurrentLocation({ timeoutMs: 10000, maxAccuracy: 100 });
    return { lat: loc.latitude, lon: loc.longitude };
  } catch (e) {
    throw new Error(tr('Nie udało się ustalić lokalizacji. Wpisz adres albo wskaż punkt na mapie.',
      'Could not get your location. Type an address or pick a point on the map.'));
  }
}
