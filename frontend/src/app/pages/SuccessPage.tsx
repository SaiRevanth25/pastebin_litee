import { useParams, Link } from "react-router";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../components/ui/card";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Check, Copy, ExternalLink } from "lucide-react";
import { useState } from "react";
import { toast } from "sonner";

export default function SuccessPage() {
  const { id } = useParams<{ id: string }>();
  const [copied, setCopied] = useState(false);

  // Generate the shareable URL using the frontend hosting URL
  const shareableUrl = `${window.location.origin}/p/${id}`;

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(shareableUrl);
      setCopied(true);
      toast.success("Link copied to clipboard!");
      setTimeout(() => setCopied(false), 2000);
    } catch (error) {
      toast.error("Failed to copy link");
      console.error(error);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 to-emerald-100 p-4 flex items-center justify-center">
      <Card className="w-full max-w-2xl shadow-lg">
        <CardHeader>
          <div className="flex items-center gap-2">
            <div className="bg-green-500 rounded-full p-2">
              <Check className="h-6 w-6 text-white" />
            </div>
            <CardTitle className="text-3xl">Paste Created!</CardTitle>
          </div>
          <CardDescription>
            Your paste has been created successfully. Share the link below.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="space-y-2">
            <label className="text-sm font-medium">Shareable Link</label>
            <div className="flex gap-2">
              <Input
                value={shareableUrl}
                readOnly
                className="font-mono"
              />
              <Button
                onClick={handleCopy}
                variant="outline"
                size="icon"
              >
                {copied ? (
                  <Check className="h-4 w-4 text-green-500" />
                ) : (
                  <Copy className="h-4 w-4" />
                )}
              </Button>
            </div>
          </div>

          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <p className="text-sm text-blue-800">
              <strong>Note:</strong> This link will expire based on your settings.
              Make sure to share it with your recipients before it expires or reaches
              the maximum view limit.
            </p>
          </div>

          <div className="flex flex-col sm:flex-row gap-3">
            <Button asChild className="flex-1">
              <Link to={`/p/${id}`}>
                <ExternalLink className="mr-2 h-4 w-4" />
                View Paste
              </Link>
            </Button>
            <Button asChild variant="outline" className="flex-1">
              <Link to="/">Create Another Paste</Link>
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
