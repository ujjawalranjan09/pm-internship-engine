import Link from "next/link";
import { APP_NAME } from "@/lib/constants";

function Footer() {
  return (
    <footer className="border-t bg-navy-500 text-white">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div>
            <div className="flex items-center gap-2 mb-3">
              <div className="h-8 w-8 rounded-lg bg-saffron-500 flex items-center justify-center">
                <span className="text-white font-bold text-sm">PM</span>
              </div>
              <span className="font-semibold">{APP_NAME}</span>
            </div>
            <p className="text-sm text-navy-200">
              AI-Based Smart Allocation Engine for PM Internship Scheme.
              Connecting talent with opportunity across India.
            </p>
          </div>

          <div>
            <h3 className="font-semibold mb-3">Quick Links</h3>
            <ul className="space-y-2 text-sm text-navy-200">
              <li><Link href="/auth/register" className="hover:text-white transition-colors">Register</Link></li>
              <li><Link href="/auth/login" className="hover:text-white transition-colors">Sign In</Link></li>
              <li><Link href="/applicant/internships" className="hover:text-white transition-colors">Browse Internships</Link></li>
            </ul>
          </div>

          <div>
            <h3 className="font-semibold mb-3">Government of India</h3>
            <ul className="space-y-2 text-sm text-navy-200">
              <li>Ministry of Skill Development and Entrepreneurship</li>
              <li>PM Internship Scheme</li>
              <li>Shram Shakti Bhawan, New Delhi</li>
            </ul>
          </div>
        </div>

        <div className="mt-8 pt-6 border-t border-navy-400 text-sm text-navy-300 flex flex-col sm:flex-row justify-between items-center gap-2">
          <p>© {new Date().getFullYear()} Government of India. All rights reserved.</p>
          <div className="flex gap-4">
            <span className="hover:text-white cursor-pointer">Privacy Policy</span>
            <span className="hover:text-white cursor-pointer">Terms of Use</span>
            <span className="hover:text-white cursor-pointer">Accessibility</span>
          </div>
        </div>
      </div>
    </footer>
  );
}

export { Footer };
