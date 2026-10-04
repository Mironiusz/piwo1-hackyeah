import { ICON_PATHS, type IconName, type IconShape } from "./iconPaths.ts";

interface IconProps {
  name: IconName;
  size?: number;
  strokeWidth?: number;
  className?: string;
}

/**
 * A line icon of the interface. It is decoration: the text next to it, or the name of its button, carries the meaning.
 */
export function Icon({ name, size = 20, strokeWidth = 2, className = "" }: IconProps) {
  const shapes: readonly IconShape[] = ICON_PATHS[name];
  return (
    <svg
      aria-hidden="true"
      focusable="false"
      viewBox="0 0 24 24"
      width={size}
      height={size}
      fill="none"
      stroke="currentColor"
      strokeWidth={strokeWidth}
      strokeLinecap="round"
      strokeLinejoin="round"
      className={`flex-none ${className}`}
    >
      {shapes.map((shape, index) => {
        if (shape.kind === "path") {
          return <path key={index} d={shape.d} />;
        }
        if (shape.kind === "circle") {
          return <circle key={index} cx={shape.cx} cy={shape.cy} r={shape.r} strokeDasharray={shape.dash} />;
        }
        return <rect key={index} x={shape.x} y={shape.y} width={shape.width} height={shape.height} rx={shape.rx} />;
      })}
    </svg>
  );
}
