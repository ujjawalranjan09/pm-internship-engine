"use client";

import { Navbar } from "@/components/shared/navbar";
import { Footer } from "@/components/shared/footer";
import { Card, CardContent } from "@/components/ui/card";

export default function AuthLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen flex flex-col">
      <Navbar />
      <main className="flex-1 flex items-center justify-center bg-gradient-to-br from-navy-50 via-white to-saffron-50 px-4 py-12">
        <div className="w-full max-w-md">
          <div className="text-center mb-8">
            <div className="mx-auto h-14 w-14 rounded-xl gov-gradient flex items-center justify-center mb-4">
              <span className="text-white font-bold text-xl">PM</span>
            </div>
            <h1 className="text-2xl font-bold text-navy-500">PM Internship Engine</h1>
            <p className="text-sm text-muted-foreground mt-1">
              AI-Based Smart Allocation for PM Internship Scheme
            </p>
          </div>
          <Card className="gov-shadow-lg">
            <CardContent className="p-6">{children}</CardContent>
          </Card>
        </div>
      </main>
      <Footer />
    </div>
  );
}
