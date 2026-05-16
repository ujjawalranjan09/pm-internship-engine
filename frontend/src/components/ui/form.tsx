"use client";

import { forwardRef, type HTMLAttributes } from "react";
import {
  useFormContext,
  type FieldValues,
  type UseFormReturn,
  type FieldPath,
  Controller,
  type ControllerProps,
} from "react-hook-form";
import { cn } from "@/lib/utils";

function Form<TFieldValues extends FieldValues = FieldValues>({
  children,
  ...formMethods
}: { children: React.ReactNode } & UseFormReturn<TFieldValues>) {
  return <form {...formMethods}>{children}</form>;
}

function FormField<
  TFieldValues extends FieldValues = FieldValues,
  TName extends FieldPath<TFieldValues> = FieldPath<TFieldValues>,
>(props: ControllerProps<TFieldValues, TName>) {
  return <Controller {...props} />;
}

const FormItem = forwardRef<HTMLDivElement, HTMLAttributes<HTMLDivElement>>(
  ({ className, ...props }, ref) => {
    return <div ref={ref} className={cn("space-y-1.5", className)} {...props} />;
  }
);
FormItem.displayName = "FormItem";

const FormLabel = forwardRef<
  HTMLLabelElement,
  HTMLAttributes<HTMLLabelElement> & { htmlFor?: string }
>(({ className, ...props }, ref) => {
  return (
    <label
      ref={ref}
      className={cn(
        "text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70",
        className
      )}
      {...props}
    />
  );
});
FormLabel.displayName = "FormLabel";

const FormControl = forwardRef<HTMLDivElement, HTMLAttributes<HTMLDivElement>>(
  ({ ...props }, ref) => {
    return <div ref={ref} {...props} />;
  }
);
FormControl.displayName = "FormControl";

const FormDescription = forwardRef<
  HTMLParagraphElement,
  HTMLAttributes<HTMLParagraphElement>
>(({ className, ...props }, ref) => {
  return (
    <p
      ref={ref}
      className={cn("text-sm text-muted-foreground", className)}
      {...props}
    />
  );
});
FormDescription.displayName = "FormDescription";

const FormMessage = forwardRef<
  HTMLParagraphElement,
  HTMLAttributes<HTMLParagraphElement> & { name?: string }
>(({ className, children, name, ...props }, ref) => {
  // Always call hooks unconditionally at the top level (Rules of Hooks)
  const methods = useFormContext();
  const fieldState =
    name && methods ? methods.getFieldState(name, methods.formState) : undefined;

  const errorContent = fieldState?.error?.message
    ? String(fieldState.error.message)
    : children;

  if (!errorContent) return null;

  return (
    <p
      ref={ref}
      className={cn("text-sm font-medium text-gov-error", className)}
      role="alert"
      {...props}
    >
      {errorContent}
    </p>
  );
});
FormMessage.displayName = "FormMessage";

export {
  Form,
  FormField,
  FormItem,
  FormLabel,
  FormControl,
  FormDescription,
  FormMessage,
};
