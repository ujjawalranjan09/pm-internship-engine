"use client";

import { createContext, useContext, useState, useRef, useEffect, type ReactNode, type ButtonHTMLAttributes } from "react";
import { cn } from "@/lib/utils";

interface DropdownMenuContextType {
  open: boolean;
  setOpen: (open: boolean) => void;
}

const DropdownMenuContext = createContext<DropdownMenuContextType>({
  open: false,
  setOpen: () => {},
});

function DropdownMenu({ children }: { children: ReactNode }) {
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) {
        setOpen(false);
      }
    };
    document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, []);

  return (
    <DropdownMenuContext.Provider value={{ open, setOpen }}>
      <div ref={ref} className="relative inline-block">{children}</div>
    </DropdownMenuContext.Provider>
  );
}

function DropdownMenuTrigger({ children, className, ...props }: ButtonHTMLAttributes<HTMLButtonElement>) {
  const { open, setOpen } = useContext(DropdownMenuContext);
  return (
    <button
      className={cn("inline-flex items-center justify-center", className)}
      onClick={() => setOpen(!open)}
      aria-expanded={open}
      aria-haspopup="true"
      {...props}
    >
      {children}
    </button>
  );
}

function DropdownMenuContent({ children, className, align = "start" }: { children: ReactNode; className?: string; align?: "start" | "end" }) {
  const { open } = useContext(DropdownMenuContext);
  if (!open) return null;

  return (
    <div
      role="menu"
      className={cn(
        "absolute z-50 mt-1 min-w-[8rem] rounded-lg border bg-background p-1 shadow-lg animate-in fade-in-0 zoom-in-95",
        align === "end" ? "right-0" : "left-0",
        className
      )}
    >
      {children}
    </div>
  );
}

function DropdownMenuItem({
  children,
  className,
  onClick,
  ...props
}: {
  children: ReactNode;
  className?: string;
  onClick?: () => void;
  disabled?: boolean;
}) {
  const { setOpen } = useContext(DropdownMenuContext);
  return (
    <button
      role="menuitem"
      className={cn(
        "relative flex w-full cursor-pointer select-none items-center rounded-md px-3 py-2 text-sm outline-none transition-colors hover:bg-muted focus:bg-muted",
        "disabled:pointer-events-none disabled:opacity-50",
        className
      )}
      onClick={() => {
        onClick?.();
        setOpen(false);
      }}
      {...props}
    >
      {children}
    </button>
  );
}

function DropdownMenuSeparator() {
  return <div className="my-1 h-px bg-muted" role="separator" />;
}

export { DropdownMenu, DropdownMenuTrigger, DropdownMenuContent, DropdownMenuItem, DropdownMenuSeparator };
