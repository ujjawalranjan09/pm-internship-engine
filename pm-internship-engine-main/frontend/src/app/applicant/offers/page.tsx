"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { Separator } from "@/components/ui/separator";
import { SkeletonCard } from "@/components/shared/skeleton";
import { PageHeader } from "@/components/shared/page-header";
import { EmptyState } from "@/components/shared/empty-state";
import { useToast } from "@/components/ui/toast";
import { formatCurrency, formatDate, cn } from "@/lib/utils";
import {
  Gift,
  MapPin,
  Clock,
  IndianRupee,
  Calendar,
  CheckCircle,
  XCircle,
  AlertTriangle,
  Briefcase,
} from "lucide-react";

interface Offer {
  id: string;
  opportunityId: string;
  title: string;
  company: string;
  sector: string;
  location: string;
  stipend: number;
  duration: number;
  startDate: string;
  endDate: string;
  status: "pending" | "accepted" | "declined" | "expired";
  offeredAt: string;
  deadline: string;
}

const MOCK_ACTIVE_OFFERS: Offer[] = [
  {
    id: "off1",
    opportunityId: "o6",
    title: "Cloud Infrastructure Intern",
    company: "CloudFirst",
    sector: "Information Technology",
    location: "Hyderabad",
    stipend: 16000,
    duration: 6,
    startDate: "2025-03-01",
    endDate: "2025-08-31",
    status: "pending",
    offeredAt: "2025-02-20T10:00:00Z",
    deadline: "2025-02-28T23:59:59Z",
  },
];

const MOCK_PAST_OFFERS: Offer[] = [
  {
    id: "off2",
    opportunityId: "o1",
    title: "Software Development Intern",
    company: "TechCorp India",
    sector: "Information Technology",
    location: "Bangalore",
    stipend: 15000,
    duration: 6,
    startDate: "2025-01-15",
    endDate: "2025-07-15",
    status: "declined",
    offeredAt: "2025-01-10T10:00:00Z",
    deadline: "2025-01-17T23:59:59Z",
  },
  {
    id: "off3",
    opportunityId: "o2",
    title: "Data Analytics Intern",
    company: "FinServ Ltd",
    sector: "Finance & Banking",
    location: "Mumbai",
    stipend: 12000,
    duration: 4,
    startDate: "2024-12-01",
    endDate: "2025-03-31",
    status: "expired",
    offeredAt: "2024-11-20T10:00:00Z",
    deadline: "2024-11-27T23:59:59Z",
  },
];

function CountdownTimer({ deadline }: { deadline: string }) {
  const [timeLeft, setTimeLeft] = useState({ days: 0, hours: 0, minutes: 0, seconds: 0 });

  useEffect(() => {
    const calculate = () => {
      const diff = new Date(deadline).getTime() - Date.now();
      if (diff <= 0) {
        setTimeLeft({ days: 0, hours: 0, minutes: 0, seconds: 0 });
        return;
      }
      setTimeLeft({
        days: Math.floor(diff / (1000 * 60 * 60 * 24)),
        hours: Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60)),
        minutes: Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60)),
        seconds: Math.floor((diff % (1000 * 60)) / 1000),
      });
    };
    calculate();
    const interval = setInterval(calculate, 1000);
    return () => clearInterval(interval);
  }, [deadline]);

  const isExpired = new Date(deadline).getTime() <= Date.now();

  if (isExpired) {
    return <span className="text-sm text-gov-error font-medium font-[var(--font-dm-sans)]">Deadline passed</span>;
  }

  return (
    <div className="flex gap-2">
      {[
        { value: timeLeft.days, label: "Days" },
        { value: timeLeft.hours, label: "Hrs" },
        { value: timeLeft.minutes, label: "Min" },
        { value: timeLeft.seconds, label: "Sec" },
      ].map((unit) => (
        <div key={unit.label} className="text-center">
          <div className="bg-[var(--role-primary-500)] text-white rounded-lg px-2.5 py-1.5 min-w-[40px]">
            <span className="text-lg font-bold font-[var(--font-space-grotesk)] tabular-nums">{String(unit.value).padStart(2, "0")}</span>
          </div>
          <span className="text-[10px] text-muted-foreground mt-0.5 block font-[var(--font-dm-sans)]">{unit.label}</span>
        </div>
      ))}
    </div>
  );
}

function OfferCard({
  offer,
  onAccept,
  onDecline,
  isProcessing,
}: {
  offer: Offer;
  onAccept: () => void;
  onDecline: () => void;
  isProcessing: boolean;
}) {
  return (
    <Card className="overflow-hidden card-hover">
      <div className={cn(
        "h-1.5",
        offer.status === "pending" ? "bg-saffron-500" :
        offer.status === "accepted" ? "bg-gov-success" :
        offer.status === "declined" ? "bg-gov-error" : "bg-muted"
      )} />
      <CardContent className="p-6">
        <div className="flex items-start justify-between mb-4">
          <div>
            <h3 className="font-semibold text-lg font-[var(--font-dm-sans)]">{offer.title}</h3>
            <p className="text-sm text-muted-foreground font-[var(--font-dm-sans)]">{offer.company}</p>
          </div>
          <Badge variant="status" status={offer.status}>
            {offer.status === "pending" ? "Action Required" : offer.status.charAt(0).toUpperCase() + offer.status.slice(1)}
          </Badge>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-4">
          <div className="flex items-center gap-2">
            <MapPin className="h-4 w-4 text-muted-foreground" />
            <div>
              <p className="text-xs text-muted-foreground font-[var(--font-dm-sans)]">Location</p>
              <p className="text-sm font-medium font-[var(--font-dm-sans)]">{offer.location}</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <IndianRupee className="h-4 w-4 text-muted-foreground" />
            <div>
              <p className="text-xs text-muted-foreground font-[var(--font-dm-sans)]">Stipend</p>
              <p className="text-sm font-medium font-[var(--font-jetbrains-mono)] tabular-nums">{formatCurrency(offer.stipend)}/mo</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Clock className="h-4 w-4 text-muted-foreground" />
            <div>
              <p className="text-xs text-muted-foreground font-[var(--font-dm-sans)]">Duration</p>
              <p className="text-sm font-medium font-[var(--font-dm-sans)]">{offer.duration} months</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Calendar className="h-4 w-4 text-muted-foreground" />
            <div>
              <p className="text-xs text-muted-foreground font-[var(--font-dm-sans)]">Start Date</p>
              <p className="text-sm font-medium font-[var(--font-dm-sans)]">{formatDate(offer.startDate)}</p>
            </div>
          </div>
        </div>

        {offer.status === "pending" && (
          <>
            <Separator className="my-4" />
            <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
              <div>
                <p className="text-sm font-medium mb-2 flex items-center gap-1 font-[var(--font-dm-sans)]">
                  <AlertTriangle className="h-4 w-4 text-gov-warning" />
                  Accept by {formatDate(offer.deadline, "dd MMM yyyy, hh:mm a")}
                </p>
                <CountdownTimer deadline={offer.deadline} />
              </div>
              <div className="flex gap-2 w-full sm:w-auto">
                <Button
                  variant="destructive"
                  onClick={onDecline}
                  loading={isProcessing}
                  className="flex-1 sm:flex-none"
                >
                  <XCircle className="h-4 w-4 mr-1" /> Decline
                </Button>
                <Button
                  onClick={onAccept}
                  loading={isProcessing}
                  className="flex-1 sm:flex-none"
                >
                  <CheckCircle className="h-4 w-4 mr-1" /> Accept Offer
                </Button>
              </div>
            </div>
          </>
        )}
      </CardContent>
    </Card>
  );
}

export default function OffersPage() {
  const { addToast } = useToast();
  const [activeOffers, setActiveOffers] = useState(MOCK_ACTIVE_OFFERS);
  const [processing, setProcessing] = useState(false);

  const handleAccept = (offerId: string) => {
    setProcessing(true);
    setTimeout(() => {
      setActiveOffers((prev) => prev.map((o) => o.id === offerId ? { ...o, status: "accepted" as const } : o));
      setProcessing(false);
      addToast({ type: "success", title: "Offer accepted!", message: "Congratulations on your internship!" });
    }, 1500);
  };

  const handleDecline = (offerId: string) => {
    setProcessing(true);
    setTimeout(() => {
      setActiveOffers((prev) => prev.map((o) => o.id === offerId ? { ...o, status: "declined" as const } : o));
      setProcessing(false);
      addToast({ type: "info", title: "Offer declined", message: "The offer has been declined." });
    }, 1000);
  };

  return (
    <div className="space-y-6 animate-fade-in">
      <PageHeader
        title="My Offers"
        description="Review and manage your internship offers"
        breadcrumbs={[{ label: "Dashboard", href: "/applicant" }, { label: "Offers" }]}
      />

      {/* Summary */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4 text-center">
            <p className="text-2xl font-bold text-saffron-600 font-[var(--font-space-grotesk)] tabular-nums">
              {activeOffers.filter((o) => o.status === "pending").length}
            </p>
            <p className="text-xs text-muted-foreground font-[var(--font-dm-sans)]">Pending</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4 text-center">
            <p className="text-2xl font-bold text-gov-success font-[var(--font-space-grotesk)] tabular-nums">
              {[...activeOffers, ...MOCK_PAST_OFFERS].filter((o) => o.status === "accepted").length}
            </p>
            <p className="text-xs text-muted-foreground font-[var(--font-dm-sans)]">Accepted</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4 text-center">
            <p className="text-2xl font-bold text-gov-error font-[var(--font-space-grotesk)] tabular-nums">
              {[...activeOffers, ...MOCK_PAST_OFFERS].filter((o) => o.status === "declined").length}
            </p>
            <p className="text-xs text-muted-foreground font-[var(--font-dm-sans)]">Declined</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4 text-center">
            <p className="text-2xl font-bold text-muted-foreground font-[var(--font-space-grotesk)] tabular-nums">
              {[...activeOffers, ...MOCK_PAST_OFFERS].filter((o) => o.status === "expired").length}
            </p>
            <p className="text-xs text-muted-foreground font-[var(--font-dm-sans)]">Expired</p>
          </CardContent>
        </Card>
      </div>

      <Tabs defaultValue="active" className="w-full">
        <TabsList className="w-full">
          <TabsTrigger value="active">
            <Gift className="h-4 w-4 mr-1.5" />
            Active Offers <span className="ml-1 h-5 w-5 rounded-full bg-saffron-500 text-white text-xs flex items-center justify-center">{activeOffers.filter((o) => o.status === "pending").length}</span>
          </TabsTrigger>
          <TabsTrigger value="history">
            <Clock className="h-4 w-4 mr-1.5" />
            Past Offers
          </TabsTrigger>
        </TabsList>

        <TabsContent value="active" className="space-y-4">
          {activeOffers.filter((o) => o.status === "pending").length === 0 ? (
            <EmptyState
              icon="inbox"
              title="No active offers"
              description="You don't have any pending offers at the moment. Keep applying to internships!"
              action={{ label: "Browse Internships", href: "/applicant/internships" }}
            />
          ) : (
            activeOffers
              .filter((o) => o.status === "pending")
              .map((offer) => (
                <OfferCard
                  key={offer.id}
                  offer={offer}
                  onAccept={() => handleAccept(offer.id)}
                  onDecline={() => handleDecline(offer.id)}
                  isProcessing={processing}
                />
              ))
          )}
        </TabsContent>

        <TabsContent value="history" className="space-y-4">
          {[...activeOffers.filter((o) => o.status !== "pending"), ...MOCK_PAST_OFFERS].length === 0 ? (
            <EmptyState
              icon="inbox"
              title="No past offers"
              description="Your offer history will appear here"
            />
          ) : (
            [...activeOffers.filter((o) => o.status !== "pending"), ...MOCK_PAST_OFFERS].map((offer) => (
              <Card key={offer.id}>
                <CardContent className="p-5">
                  <div className="flex items-start justify-between mb-3">
                    <div>
                      <h3 className="font-semibold font-[var(--font-dm-sans)]">{offer.title}</h3>
                      <p className="text-sm text-muted-foreground font-[var(--font-dm-sans)]">{offer.company} · {offer.location}</p>
                    </div>
                    <Badge variant="status" status={offer.status}>
                      {offer.status.charAt(0).toUpperCase() + offer.status.slice(1)}
                    </Badge>
                  </div>
                  <div className="flex flex-wrap gap-4 text-sm text-muted-foreground font-[var(--font-dm-sans)]">
                    <span className="flex items-center gap-1">
                      <IndianRupee className="h-3.5 w-3.5" /> {formatCurrency(offer.stipend)}/mo
                    </span>
                    <span className="flex items-center gap-1">
                      <Clock className="h-3.5 w-3.5" /> {offer.duration} months
                    </span>
                    <span className="flex items-center gap-1">
                      <Briefcase className="h-3.5 w-3.5" /> {offer.sector}
                    </span>
                  </div>
                </CardContent>
              </Card>
            ))
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
}