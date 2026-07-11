"use client";

import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { feedbackSchema, type FeedbackFormData } from "@/lib/validators";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { Tabs } from "@/components/ui/tabs";
import { PageHeader } from "@/components/shared/page-header";
import { EmptyState } from "@/components/shared/empty-state";
import { useToast } from "@/components/ui/toast";
import { formatDate, cn } from "@/lib/utils";
import {
  Star,
  Send,
  MessageSquare,
  Clock,
  User,
  CheckCircle,
} from "lucide-react";

const MOCK_INTERNS = [
  { id: "c6", name: "Arjun Reddy", internship: "Cloud Infrastructure Intern", startDate: "2025-01-15" },
  { id: "c1", name: "Priya Sharma", internship: "Software Development Intern", startDate: "2025-01-15" },
];

const MOCK_PAST_FEEDBACK = [
  {
    id: "f1",
    internName: "Arjun Reddy",
    internship: "Cloud Infrastructure Intern",
    rating: 4,
    areas: { technical: 4, communication: 3, teamwork: 5, initiative: 4, punctuality: 4 },
    comment: "Arjun has shown excellent technical aptitude and is a great team player. He proactively took on additional responsibilities.",
    submittedAt: "2025-02-10T10:00:00Z",
  },
  {
    id: "f2",
    internName: "Priya Sharma",
    internship: "Software Development Intern",
    rating: 5,
    areas: { technical: 5, communication: 5, teamwork: 4, initiative: 5, punctuality: 5 },
    comment: "Outstanding performance. Priya delivered high-quality code and mentored newer interns.",
    submittedAt: "2025-01-28T14:00:00Z",
  },
];

function StarRating({ value, onChange, label }: { value: number; onChange?: (v: number) => void; label: string }) {
  return (
    <div className="flex items-center gap-1" role="group" aria-label={label}>
      {[1, 2, 3, 4, 5].map((star) => (
        <button
          key={star}
          type="button"
          onClick={() => onChange?.(star)}
          disabled={!onChange}
          className={cn(
            "p-0.5 transition-colors",
            onChange && "cursor-pointer hover:scale-110"
          )}
          aria-label={`${star} star${star !== 1 ? "s" : ""}`}
        >
          <Star
            className={cn(
              "h-5 w-5",
              star <= value ? "text-saffron-500 fill-current" : "text-gray-300"
            )}
          />
        </button>
      ))}
    </div>
  );
}

function FeedbackForm() {
  const { addToast } = useToast();
  const [candidateId, setCandidateId] = useState("");
  const [rating, setRating] = useState(0);
  const [comment, setComment] = useState("");
  const [areas, setAreas] = useState({ technical: 0, communication: 0, teamwork: 0, initiative: 0, punctuality: 0 });
  const [submitting, setSubmitting] = useState(false);

  const selectedIntern = MOCK_INTERNS.find((i) => i.id === candidateId);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!candidateId || rating === 0 || comment.length < 10) {
      addToast({ type: "warning", title: "Incomplete form", message: "Please fill all required fields." });
      return;
    }
    setSubmitting(true);
    setTimeout(() => {
      setSubmitting(false);
      addToast({ type: "success", title: "Feedback submitted", message: "Thank you for your feedback!" });
      setCandidateId("");
      setRating(0);
      setComment("");
      setAreas({ technical: 0, communication: 0, teamwork: 0, initiative: 0, punctuality: 0 });
    }, 1500);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Select Intern</CardTitle>
        </CardHeader>
        <CardContent>
          <Select
            label="Intern"
            options={[
              { label: "Select an intern...", value: "" },
              ...MOCK_INTERNS.map((i) => ({ label: `${i.name} — ${i.internship}`, value: i.id })),
            ]}
            value={candidateId}
            onChange={(e) => setCandidateId(e.target.value)}
          />
          {selectedIntern && (
            <div className="mt-3 p-3 rounded-lg bg-muted/50 flex items-center gap-3">
              <User className="h-5 w-5 text-muted-foreground" />
              <div>
                <p className="text-sm font-medium">{selectedIntern.name}</p>
                <p className="text-xs text-muted-foreground">{selectedIntern.internship} · Started {formatDate(selectedIntern.startDate)}</p>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Overall Rating</CardTitle>
          <CardDescription>Rate the intern&apos;s overall performance</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center gap-4">
            <StarRating value={rating} onChange={setRating} label="Overall rating" />
            {rating > 0 && (
              <span className="text-lg font-bold text-navy-600">{rating}/5</span>
            )}
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Performance Areas</CardTitle>
          <CardDescription>Rate each area individually</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {Object.entries(areas).map(([key, val]) => (
            <div key={key} className="flex items-center justify-between">
              <span className="text-sm font-medium capitalize">{key}</span>
              <StarRating
                value={val}
                onChange={(v) => setAreas((prev) => ({ ...prev, [key]: v }))}
                label={key}
              />
            </div>
          ))}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Comments</CardTitle>
          <CardDescription>Provide detailed feedback about the intern&apos;s performance</CardDescription>
        </CardHeader>
        <CardContent>
          <label className="block text-sm font-medium mb-1.5">
            Feedback Comments <span className="text-gov-error">*</span>
          </label>
          <textarea
            value={comment}
            onChange={(e) => setComment(e.target.value)}
            rows={5}
            className="w-full rounded-lg border bg-background px-3 py-2 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-navy-500"
            placeholder="Describe the intern's strengths, areas for improvement, and overall assessment..."
          />
          <p className="text-xs text-muted-foreground mt-1">{comment.length}/10 minimum characters</p>
        </CardContent>
      </Card>

      <div className="flex justify-end">
        <Button type="submit" loading={submitting}>
          <Send className="h-4 w-4 mr-2" /> Submit Feedback
        </Button>
      </div>
    </form>
  );
}

function FeedbackHistory() {
  return (
    <div className="space-y-4">
      {MOCK_PAST_FEEDBACK.length === 0 ? (
        <EmptyState
          icon="inbox"
          title="No feedback submitted yet"
          description="Your feedback history will appear here"
        />
      ) : (
        MOCK_PAST_FEEDBACK.map((fb) => (
          <Card key={fb.id}>
            <CardContent className="p-5">
              <div className="flex items-start justify-between mb-3">
                <div>
                  <h3 className="font-semibold">{fb.internName}</h3>
                  <p className="text-sm text-muted-foreground">{fb.internship}</p>
                </div>
                <div className="flex items-center gap-2">
                  <StarRating value={fb.rating} label="Rating" />
                  <span className="text-sm font-bold">{fb.rating}/5</span>
                </div>
              </div>
              <p className="text-sm text-muted-foreground mb-3">{fb.comment}</p>
              <div className="flex flex-wrap gap-2">
                {Object.entries(fb.areas).map(([key, val]) => (
                  <Badge key={key} variant="outline" size="sm">
                    {key}: {val}/5
                  </Badge>
                ))}
              </div>
              <p className="text-xs text-muted-foreground mt-3 flex items-center gap-1">
                <Clock className="h-3 w-3" /> Submitted {formatDate(fb.submittedAt, "dd MMM yyyy")}
              </p>
            </CardContent>
          </Card>
        ))
      )}
    </div>
  );
}

export default function FeedbackPage() {
  const tabs = [
    {
      id: "submit",
      label: "Submit Feedback",
      icon: <MessageSquare className="h-4 w-4" />,
      content: <FeedbackForm />,
    },
    {
      id: "history",
      label: "Feedback History",
      icon: <Clock className="h-4 w-4" />,
      content: <FeedbackHistory />,
    },
  ];

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <PageHeader
        title="Intern Feedback"
        description="Submit and manage feedback for your interns"
        breadcrumbs={[{ label: "Dashboard", href: "/employer" }, { label: "Feedback" }]}
      />
      <Tabs tabs={tabs} defaultTab="submit" />
    </div>
  );
}
