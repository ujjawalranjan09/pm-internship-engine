# Type-Check Errors Report
## PM Internship Engine Repository

**Report Generated:** May 16, 2026  
**Analysis Scope:** Frontend TypeScript (tsc), Backend Python (MyPy), GitHub Actions CI

---

## Executive Summary

The pm-internship-engine repository has **46+ TypeScript type-check errors** that are preventing the GitHub Actions CI pipeline from passing. These errors are primarily caused by:

1. **Missing type exports** in validation and type definition files
2. **Type mismatches** in interface definitions (FairnessMetrics)
3. **Function signature mismatches** (formatDate, mutation handlers)
4. **Component prop type incompatibilities** (EmptyState action prop)
5. **Array vs callable type issues** in form handling
6. **Union type property access errors** in components

---

## FRONTEND - TypeScript Errors (46 Total)

### Error Category 1: Missing Type Exports (8 errors)

#### Files Affected:
- `frontend/src/lib/validators.ts`
- `frontend/src/types/common.ts`
- `frontend/src/types/allocation.ts`

#### Issues:

**Error: Module '"@/lib/validators"' has no exported member 'ProfileFormData'**
```
Location: src/app/applicant/profile/page.tsx:7
Import: import { profileSchema, type ProfileFormData } from "@/lib/validators";
Current State: validators.ts exports ProfileInput, not ProfileFormData
```

**Error: Module '"@/lib/validators"' has no exported member 'LoginFormData'**
```
Location: src/app/auth/login/page.tsx:7
Import: import { loginSchema, type LoginFormData } from "@/lib/validators";
Current State: validators.ts exports LoginInput, not LoginFormData
```

**Error: Module '"@/lib/validators"' has no exported member 'RegisterFormData'**
```
Location: src/app/auth/register/page.tsx:7
Import: import { registerSchema, type RegisterFormData } from "@/lib/validators";
Current State: validators.ts exports RegisterInput, not RegisterFormData
```

**Error: Module '"@/lib/validators"' has no exported member 'FeedbackFormData'**
```
Location: src/app/employer/feedback/page.tsx:6
Import: import { feedbackSchema, type FeedbackFormData } from "@/lib/validators";
Current State: validators.ts exports FeedbackInput, not FeedbackFormData
```

**Error: Module '"@/lib/validators"' has no exported member 'opportunitySchema' / 'OpportunityFormData'**
```
Location: src/app/employer/internships/new/page.tsx:8
Import: import { opportunitySchema, type OpportunityFormData } from "@/lib/validators";
Current State: validators.ts exports internshipSchema and InternshipInput, not opportunitySchema/OpportunityFormData
```

**Error: Module '"@/types/common"' has no exported member 'UserRole'**
```
Location: src/types/user.ts:1
Import: import type { UserRole } from "./common";
Current State: UserRole type is not defined in common.ts
Fix: Define UserRole in common.ts: export type UserRole = "applicant" | "employer" | "admin";
```

**Error: Module '"@/types/common"' has no exported member 'ApiError'**
```
Location: src/services/api-client.ts:2
Import: import type { ApiError } from "@/types/common";
Current State: ApiError type is not defined in common.ts
Fix: Define ApiError interface in common.ts
```

**Error: Module '"@/types/allocation"' has no exported member 'PolicyConfig', 'AuditEntry', 'OverrideRequest'**
```
Location: src/services/admin-service.ts:4
Import: import { PolicyConfig, AuditEntry, OverrideRequest } from "@/types/allocation";
Current State: allocation.ts doesn't export these types
Fix: Add these type definitions to allocation.ts
```

---

### Error Category 2: FairnessMetrics Type Incompleteness (8 errors)

#### Root Cause:
`FairnessMetrics` interface in `src/types/allocation.ts` is missing properties that are being accessed throughout the codebase.

#### Current FairnessMetrics Definition:
```typescript
export interface FairnessMetrics {
  representationIndex: number;
  categoryDistribution: Record<string, number>;
  genderDistribution: Record<string, number>;
  ruralUrbanRatio: { rural: number; urban: number };
}
```

#### Missing Properties:
- `stateDistribution: Record<string, number>` (referenced in multiple files)
- `districtDistribution: Record<string, number>` (referenced in multiple files)

#### Specific Errors:

**Error TS2339: Property 'stateDistribution' does not exist on type 'FairnessMetrics'**
```
src/app/admin/fairness/page.tsx:44
  const stateEntries = Object.entries(metrics.stateDistribution).sort(([, a], [, b]) => b - a);
                                                 ~~~~~~~~~~~~~~~~~

src/app/admin/fairness/page.tsx:193
  <div style={{ width: `${(pct / stateEntries[0][1]) * 100}%` }} />
                                  ~~~~~~~~~~~~~~~~~~
```

**Error TS2339: Property 'districtDistribution' does not exist on type 'FairnessMetrics'**
```
src/app/admin/fairness/page.tsx:45
  const districtEntries = Object.entries(metrics.districtDistribution).sort(([, a], [, b]) => b - a);
                                                 ~~~~~~~~~~~~~~~~~~~~
```

**Error TS2353: Object literal may only specify known properties, and 'stateDistribution' does not exist**
```
src/services/admin-service.ts:127
  Mock data creating FairnessMetrics with stateDistribution property

src/services/allocation-service.ts:17, 37, 56
  Mock data creating FairnessMetrics with stateDistribution property
```

#### Type Inference Errors from Missing Properties:
```
src/app/admin/fairness/page.tsx:193
error TS18046: 'pct' is of type 'unknown'.
error TS2571: Object is of type 'unknown'.

src/app/admin/fairness/page.tsx:195
error TS2322: Type 'unknown' is not assignable to type 'ReactNode'.
```

---

### Error Category 3: Function Signature Mismatches (4 errors)

#### Error: Expected 1-2 arguments, but got 0

**Location: src/app/admin/allocation/page.tsx:57**
```typescript
error TS2554: Expected 1-2 arguments, but got 0.

triggerAllocation.mutate();
                 ~~~~~~

Expected Type:
declare type UseMutateFunction<TData = unknown, TError = DefaultError, TVariables = void, TOnMutateResult = unknown> = 
  (...args: Parameters<MutateFunction<TData, TError, TVariables, TOnMutateResult>>) => void;
```

**Fix:** The mutation requires variables to be passed. Should be:
```typescript
triggerAllocation.mutate(payload); // where payload matches TVariables type
```

---

#### Error: Expected 0-1 arguments, but got 2

**formatDate function signature issue**

**Locations:**
- src/app/applicant/applications/page.tsx:224
  ```typescript
  {formatDate(event.date, "dd MMM yyyy, hh:mm a")}
                         ~~~~~~~~~~~~~~~~~~~~~~
  error TS2554: Expected 0-1 arguments, but got 2.
  ```

- src/app/applicant/applications/page.tsx:314
  ```typescript
  {formatDate(event.date, "dd MMM yyyy, hh:mm a")}
                         ~~~~~~~~~~~~~~~~~~~~~~
  ```

- src/app/applicant/offers/page.tsx:208
  ```typescript
  Accept by {formatDate(offer.deadline, "dd MMM yyyy, hh:mm a")}
                                        ~~~~~~~~~~~~~~~~~~~~~~
  ```

- src/app/employer/feedback/page.tsx:230
  ```typescript
  {formatDate(event.date, "dd MMM yyyy, hh:mm a")}
  ```

**Fix:** Check the formatDate function signature. It seems to be defined without the format parameter. Update the function definition to accept a format string:
```typescript
export function formatDate(date: string | Date, format?: string): string
```

---

### Error Category 4: Component Prop Type Incompatibilities (2 errors)

#### Error: 'href' does not exist in type '{ label: string; onClick: () => void; }'

**Locations:**
- src/app/applicant/allocations/page.tsx:57
  ```typescript
  action={{ label: "View Matches", href: "/applicant/matches" }}
                                    ~~~~
  error TS2353: Object literal may only specify known properties, and 'href' does not exist
  ```

- src/app/applicant/matches/page.tsx:58
  ```typescript
  action={{ label: "Complete Profile", href: "/applicant/profile" }}
                                        ~~~~
  ```

**Root Cause:**
`EmptyState` component's action prop is defined in `src/components/shared/empty-state.tsx:11` as:
```typescript
action?: {
  label: string;
  onClick: () => void;
}
```

But code is trying to pass `href` property for navigation.

**Fix:** Update ActionConfig interface in `src/types/common.ts` (already has href but EmptyState isn't using it). Update EmptyState to properly handle href:
```typescript
action?: {
  label: string;
  onClick?: () => void;
  href?: string;
}
```

---

### Error Category 5: Array vs Callable Type Issues (3 errors)

#### Error: Type 'string[]' has no call signatures

**Locations:**
- src/app/applicant/profile/page.tsx:85
  ```typescript
  error TS2349: This expression is not callable.
  Type 'string[]' has no call signatures.
  ```

- src/app/applicant/profile/page.tsx:328
  ```typescript
  Same error
  ```

- src/app/employer/internships/new/page.tsx:71
  ```typescript
  Same error
  ```

**Root Cause:** Variables defined as arrays but being called as functions. Usually happens with form field error handlers.

**Fix:** Review the code at these locations to verify whether the variable should be an array or a function. If it's form field errors, ensure proper typing:
```typescript
// If it's an array of errors:
errors: string[]

// If it should be a function:
getErrors: (fieldName: string) => string[]
```

---

### Error Category 6: Union Type Property Access (2 errors)

#### Error: Property 'map' does not exist on union type

**Location: src/components/shared/navbar.tsx:44, 114**
```typescript
error TS2339: Property 'map' does not exist on type '{ readonly label: "Home"; readonly href: "/"; } | ...'
Property 'map' does not exist on type '{ readonly label: "Home"; readonly href: "/"; }'.
```

**Root Cause:** Navigation items are defined as union types, but only some members of the union have the map method (arrays only).

**Fix:** Ensure navigation items are consistently typed as arrays or properly type guard before using map:
```typescript
// Should be:
const navItems: NavItem[] = [...]

// Not:
const navItems: NavItem | NavItem[] = ...
```

---

### Error Category 7: AllocationResult Type Mismatch (5 errors)

#### Error: Missing properties from AllocationResult type

**Location: src/services/allocation-service.ts:67-71**

```typescript
error TS2739: Type '{ id: string; cycleId: string; ... }' is missing the following properties 
from type 'AllocationResult': location, sector, stipend, allocationScore
```

**Lines:**
- Line 67: Mock allocation result
- Line 68: Mock allocation result
- Line 69: Mock allocation result
- Line 70: Mock allocation result
- Line 71: Mock allocation result

**Root Cause:** Mock data objects are missing required properties defined in AllocationResult interface.

**Required Properties in AllocationResult:**
```typescript
export interface AllocationResult {
  id: string;
  cycleId: string;
  candidateId: string;
  candidateName: string;
  opportunityId: string;
  opportunityTitle: string;
  employerName: string;
  location: string;              // <- MISSING
  sector: string;                // <- MISSING
  stipend: number;               // <- MISSING
  allocationScore: number;       // <- MISSING
  matchScore: number;
  status: AllocationStatus;
  allocatedAt: string;
  confirmedAt?: string;
  declinedAt?: string;
}
```

**Fix:** Update all mock allocation result objects to include these required fields.

---

## BACKEND - Python Type Errors

### Analysis Approach

MyPy type checking on the backend is configured with many suppressed error codes (see `backend/pyproject.toml`):

```toml
[tool.mypy]
python_version = "3.12"
strict = true
ignore_missing_imports = true

disable_error_code = [
  "type-arg",
  "no-untyped-def",
  "unused-ignore",
  "attr-defined",
  "assignment",
  "return-value",
  "arg-type",
  "index",
  "operator",
  "misc",
  "var-annotated",
  "type-var",
  "no-untyped-call",
  "truthy-function",
]
```

### Likely Issues (Based on Configuration)

1. **Generic Type Arguments**: Many types likely missing explicit type parameters (type-arg disabled)
2. **Function Return Types**: Functions may not have explicit return type annotations (no-untyped-def disabled)
3. **Assignment Compatibility**: Incompatible type assignments may be present (assignment disabled)
4. **Function Call Type Checking**: Untyped function calls in typed contexts (no-untyped-call disabled)

### Recommendation

To identify actual MyPy errors:
```bash
cd backend
python -m mypy app/ --show-error-codes --config-file pyproject.toml
```

**Note:** Full MyPy run can take 1-2 minutes on slower systems due to type stub resolution.

---

## CI/CD Integration

### GitHub Actions Workflow: `.github/workflows/ci.yml`

**Relevant Jobs:**
1. **backend-lint** - Ruff linting (requires: None, passes to lint)
2. **backend-typecheck** - MyPy type checking (requires: backend-lint)
3. **backend-test** - Pytest (requires: backend-lint)
4. **frontend-lint** - ESLint (requires: None)
5. **frontend-typecheck** - TypeScript tsc (requires: frontend-lint) ⚠️ **FAILING**
6. **frontend-build** - Next.js build (requires: frontend-lint, frontend-typecheck)

**Current Blocker:** Frontend TypeScript type checking fails, preventing build job from running.

---

## Summary of Required Fixes

### Priority 1 - Critical (Blocking CI)

1. **Add missing type exports to `src/types/allocation.ts`**
   - Add `stateDistribution` and `districtDistribution` to FairnessMetrics
   - Export: `PolicyConfig`, `AuditEntry`, `OverrideRequest`

2. **Fix type exports in `src/lib/validators.ts`**
   - Rename exported types: `LoginInput` → `LoginFormData`, etc.
   - OR: Add type aliases for backward compatibility

3. **Add missing types to `src/types/common.ts`**
   - Export `UserRole` type
   - Export `ApiError` interface

4. **Update `src/components/shared/empty-state.tsx`**
   - Add `href` property support to action prop

### Priority 2 - High

5. **Fix formatDate function signature**
   - Ensure it accepts optional format parameter

6. **Fix React Query mutation calls**
   - Pass required variables to mutate()

7. **Fix AllocationResult mock data**
   - Add missing required properties

### Priority 3 - Medium

8. **Fix union type property access in navbar**
   - Ensure consistent typing

9. **Review and fix callable vs array type issues**
   - Check form error handling implementations

10. **Backend MyPy**
    - Run full type check after frontend is fixed
    - Address any remaining type errors outside disabled codes

---

## Error Count Summary

| Category | Count | Severity |
|----------|-------|----------|
| Missing Type Exports | 8 | Critical |
| FairnessMetrics Issues | 8 | Critical |
| Function Signature | 4 | High |
| Component Props | 2 | High |
| Callable vs Array | 3 | Medium |
| Union Type Access | 2 | Medium |
| AllocationResult | 5 | High |
| **Total Frontend** | **46** | **BLOCKING** |
| Backend (MyPy) | Unknown | TBD |

---

## Files Requiring Changes

### Type Definition Files
- [ ] `frontend/src/types/allocation.ts`
- [ ] `frontend/src/types/common.ts`
- [ ] `frontend/src/lib/validators.ts`
- [ ] `frontend/src/types/user.ts`

### Component Files
- [ ] `frontend/src/components/shared/empty-state.tsx`
- [ ] `frontend/src/components/shared/navbar.tsx`

### Service Files
- [ ] `frontend/src/services/admin-service.ts`
- [ ] `frontend/src/services/allocation-service.ts`
- [ ] `frontend/src/services/api-client.ts`

### Page Files
- [ ] `frontend/src/app/admin/allocation/page.tsx`
- [ ] `frontend/src/app/admin/fairness/page.tsx`
- [ ] `frontend/src/app/applicant/allocations/page.tsx`
- [ ] `frontend/src/app/applicant/applications/page.tsx`
- [ ] `frontend/src/app/applicant/matches/page.tsx`
- [ ] `frontend/src/app/applicant/offers/page.tsx`
- [ ] `frontend/src/app/applicant/profile/page.tsx`
- [ ] `frontend/src/app/auth/login/page.tsx`
- [ ] `frontend/src/app/auth/register/page.tsx`
- [ ] `frontend/src/app/employer/feedback/page.tsx`
- [ ] `frontend/src/app/employer/internships/new/page.tsx`

---

## Next Steps

1. **Immediate Action:** Fix the 8 missing type exports (most critical blocker)
2. **Second Wave:** Update FairnessMetrics interface and mock data
3. **Third Wave:** Fix function signatures and component props
4. **Validation:** Run `npm run type-check` in frontend to verify fixes
5. **Backend:** Run full MyPy check after frontend is resolved
6. **Final:** Commit and push to trigger GitHub Actions CI pipeline

