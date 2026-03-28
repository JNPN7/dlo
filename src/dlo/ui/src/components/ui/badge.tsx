import * as React from "react"
import { cva, type VariantProps } from "class-variance-authority"

import { cn } from "@/lib/utils"

const badgeVariants = cva(
  "inline-flex items-center rounded-md border px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2",
  {
    variants: {
      variant: {
        default:
          "border-transparent bg-primary text-primary-foreground shadow hover:bg-primary/80",
        secondary:
          "border-transparent bg-secondary text-secondary-foreground hover:bg-secondary/80",
        destructive:
          "border-transparent bg-destructive text-destructive-foreground shadow hover:bg-destructive/80",
        outline: "text-foreground",
        source:
          "border-transparent bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200",
        model:
          "border-transparent bg-pink-100 text-pink-800 dark:bg-pink-900 dark:text-pink-200",
        relationship:
          "border-transparent bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200",
        metric:
          "border-transparent bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200",
        materialized:
          "border-transparent bg-emerald-100 text-emerald-800 dark:bg-emerald-900 dark:text-emerald-200",
        view:
          "border-transparent bg-amber-100 text-amber-800 dark:bg-amber-900 dark:text-amber-200",
        ephemeral:
          "border-transparent bg-slate-100 text-slate-800 dark:bg-slate-900 dark:text-slate-200",
      },
    },
    defaultVariants: {
      variant: "default",
    },
  }
)

export interface BadgeProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof badgeVariants> {}

function Badge({ className, variant, ...props }: BadgeProps) {
  return (
    <div className={cn(badgeVariants({ variant }), className)} {...props} />
  )
}

export { Badge, badgeVariants }
