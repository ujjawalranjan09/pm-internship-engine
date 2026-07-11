import { cn, getInitials } from "@/lib/utils";

interface AvatarProps {
  name: string;
  src?: string;
  size?: "sm" | "md" | "lg" | "xl";
  className?: string;
}

const sizes = {
  sm: "h-8 w-8 text-xs",
  md: "h-10 w-10 text-sm",
  lg: "h-12 w-12 text-base",
  xl: "h-16 w-16 text-lg",
};

function Avatar({ name, src, size = "md", className }: AvatarProps) {
  const initials = getInitials(name);

  return (
    <div
      className={cn(
        "relative inline-flex items-center justify-center rounded-full bg-navy-100 text-navy-700 font-medium shrink-0 overflow-hidden",
        sizes[size],
        className
      )}
      aria-label={name}
    >
      {src ? (
        <img src={src} alt={name} className="h-full w-full object-cover" />
      ) : (
        <span>{initials}</span>
      )}
    </div>
  );
}

export { Avatar };
