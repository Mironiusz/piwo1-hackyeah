import { common } from '@kit.AbilityKit';
import { fileIo } from '@kit.CoreFileKit';
import { util } from '@kit.ArkTS';

export function readFileText(path: string): string | null {
  try {
    if (!fileIo.accessSync(path)) {
      return null;
    }
    return fileIo.readTextSync(path);
  } catch (e) {
    return null;
  }
}

/** Zapis przez plik tymczasowy i zmianę nazwy, żeby przerwany zapis nie zostawił uciętego pliku. */
export function writeFileText(path: string, text: string): void {
  const tmp = `${path}.tmp`;
  const f = fileIo.openSync(tmp, fileIo.OpenMode.CREATE | fileIo.OpenMode.READ_WRITE | fileIo.OpenMode.TRUNC);
  try {
    fileIo.writeSync(f.fd, text);
  } finally {
    fileIo.closeSync(f);
  }
  fileIo.renameSync(tmp, path);
}

export function removeFile(path: string): void {
  try {
    if (fileIo.accessSync(path)) {
      fileIo.unlinkSync(path);
    }
  } catch (e) {
    return;
  }
}

export function readRawText(ctx: common.Context, name: string): string | null {
  try {
    const bytes = ctx.resourceManager.getRawFileContentSync(name);
    return util.TextDecoder.create('utf-8').decodeToString(bytes);
  } catch (e) {
    return null;
  }
}
