"use client";

import { useState } from "react";
import { useNotifications, useSendNotification } from "@/hooks/use-notifications";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { Tabs } from "@/components/ui/tabs";
import { SkeletonCard } from "@/components/shared/skeleton";
import { PageHeader } from "@/components/shared/page-header";
import { EmptyState } from "@/components/shared/empty-state";
import { useToast } from "@/components/ui/toast";
import { formatRelativeTime, cn } from "@/lib/utils";
import {
  Bell,
  Send,
  CheckCircle,
  AlertCircle,
  AlertTriangle,
  Info,
  Mail,
  MailOpen,
  Filter,
} from "lucide-react";

const typeIcons: Record<string, React.ReactNode> = {
  success: <CheckCircle className="h-4 w-4 text-gov-success" />,
  error: <AlertCircle className="h-4 w-4 text-gov-error" />,
  warning: <AlertTriangle className="h-4 w-4 text-gov-warning" />,
  info: <Info className="h-4 w-4 text-gov-info" />,
};

const typeStyles: Record<string, string> = {
  success: "border-l-4 border-gov-success",
  error: "border-l-4 border-gov-error",
  warning: "border-l-4 border-gov-warning",
  info: "border-l-4 border-gov-info",
};

export default function NotificationsPage() {
  const { data: notifications, isLoading } = useNotifications();
  const sendNotification = useSendNotification();
  const { addToast } = useToast();
  const [typeFilter, setTypeFilter] = useState("");
  const [readFilter, setReadFilter] = useState<"all" | "read" | "unread">("all");
  const [subject, setSubject] = useState("");
  const [message, setMessage] = useState("");
  const [recipients, setRecipients] = useState("all");

  const filtered = (notifications ?? []).filter((n) => {
    const matchesType = !typeFilter || n.type === typeFilter;
    const matchesRead = readFilter === "all" || (readFilter === "read" ? n.read : !n.read);
    return matchesType && matchesRead;
  });

  const unreadCount = (notifications ?? []).filter((n) => !n.read).length;

  const handleSend = (e: React.FormEvent) => {
    e.preventDefault();
    if (!subject || !message) {
      addToast({ type: "warning", title: "Incomplete form", message: "Please fill subject and message." });
      return;
    }
    sendNotification.mutate(
      { subject, message, recipients },
      {
        onSuccess: () => {
          addToast({ type: "success", title: "Notification sent", message: `Sent to ${recipients === "all" ? "all users" : recipients}.` });
          setSubject("");
          setMessage("");
        },
      }
    );
  };

  const markAsRead = (id: string) => {
    addToast({ type: "info", title: "Marked as read" });
  };

  const notificationsTab = {
    id: "list",
    label: `Notifications (${(notifications ?? []).length})`,
    icon: <Bell className="h-4 w-4" />,
    content: (
      <div className="space-y-4">
        {/* Filters */}
        <div className="flex flex-wrap gap-2">
          <Select
            options={[
              { label: "All Types", value: "" },
              { label: "Info", value: "info" },
              { label: "Success", value: "success" },
              { label: "Warning", value: "warning" },
              { label: "Error", value: "error" },
            ]}
            value={typeFilter}
            onChange={(e) => setTypeFilter(e.target.value)}
            aria-label="Filter by type"
          />
          <Select
            options={[
              { label: "All", value: "all" },
              { label: "Unread", value: "unread" },
              { label: "Read", value: "read" },
            ]}
            value={readFilter}
            onChange={(e) => setReadFilter(e.target.value as "all" | "read" | "unread")}
            aria-label="Filter by read status"
          />
          {unreadCount > 0 && (
            <Badge variant="outline" className="self-center">
              {unreadCount} unread
            </Badge>
          )}
        </div>

        {isLoading ? (
          <SkeletonCard />
        ) : filtered.length === 0 ? (
          <EmptyState icon="inbox" title="No notifications" description="You're all caught up!" />
        ) : (
          <div className="space-y-2">
            {filtered.map((notif) => (
              <div
                key={notif.id}
                className={cn(
                  "flex items-start gap-3 p-4 rounded-lg border transition-colors",
                  typeStyles[notif.type],
                  !notif.read && "bg-muted/30"
                )}
              >
                <div className="mt-0.5">{typeIcons[notif.type]}</div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-start justify-between gap-2">
                    <p className={cn("text-sm", !notif.read && "font-semibold")}>{notif.title}</p>
                    {!notif.read && (
                      <div className="h-2 w-2 rounded-full bg-saffron-500 shrink-0 mt-1.5" />
                    )}
                  </div>
                  <p className="text-xs text-muted-foreground mt-0.5">{notif.message}</p>
                  <p className="text-xs text-muted-foreground mt-1">{formatRelativeTime(notif.timestamp)}</p>
                </div>
                {!notif.read && (
                  <Button variant="ghost" size="sm" onClick={() => markAsRead(notif.id)} aria-label="Mark as read">
                    <MailOpen className="h-4 w-4" />
                  </Button>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    ),
  };

  const sendTab = {
    id: "send",
    label: "Send Notification",
    icon: <Send className="h-4 w-4" />,
    content: (
      <Card>
        <CardHeader>
          <CardTitle>Send Bulk Notification</CardTitle>
          <CardDescription>Broadcast a message to users</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSend} className="space-y-4">
            <Select
              label="Recipients"
              options={[
                { label: "All Users", value: "all" },
                { label: "All Candidates", value: "candidates" },
                { label: "All Employers", value: "employers" },
                { label: "Specific Candidates (allocated)", value: "allocated_candidates" },
              ]}
              value={recipients}
              onChange={(e) => setRecipients(e.target.value)}
            />
            <Input
              label="Subject"
              value={subject}
              onChange={(e) => setSubject(e.target.value)}
              placeholder="Notification subject"
              required
            />
            <div>
              <label className="block text-sm font-medium mb-1.5">
                Message <span className="text-gov-error">*</span>
              </label>
              <textarea
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                rows={5}
                className="w-full rounded-lg border bg-background px-3 py-2 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-navy-500"
                placeholder="Type your notification message..."
                required
              />
            </div>
            <div className="flex justify-end">
              <Button type="submit" loading={sendNotification.isPending}>
                <Send className="h-4 w-4 mr-2" /> Send Notification
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>
    ),
  };

  return (
    <div className="space-y-6">
      <PageHeader
        title="Notifications"
        description="Manage system notifications and send broadcasts"
      />
      <Tabs tabs={[notificationsTab, sendTab]} defaultTab="list" />
    </div>
  );
}
