import { useState } from "react";
import { useNavigate } from "react-router";
import { Button } from "../components/ui/button";
import { Textarea } from "../components/ui/textarea";
import { Label } from "../components/ui/label";
import { Input } from "../components/ui/input";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../components/ui/card";
import { createPaste } from "../utils/api";
import { toast } from "sonner";
import { Loader2 } from "lucide-react";

export default function CreatePaste() {
  const [content, setContent] = useState("");
  const [ttlSeconds, setTtlSeconds] = useState("3600");
  const [maxViews, setMaxViews] = useState("100");
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!content.trim()) {
      toast.error("Please enter some content");
      return;
    }

    setIsLoading(true);

    try {
      const response = await createPaste({
        content: content.trim(),
        ttl_seconds: parseInt(ttlSeconds) || 3600,
        max_views: parseInt(maxViews) || 100,
      });

      toast.success("Paste created successfully!");
      navigate(`/success/${response.id}`);
    } catch (error) {
      toast.error("Failed to create paste. Please try again.");
      console.error(error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-4 flex items-center justify-center">
      <Card className="w-full max-w-3xl shadow-lg">
        <CardHeader>
          <CardTitle className="text-3xl">Create a Paste</CardTitle>
          <CardDescription>
            Share text snippets with expiration time and view limits
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="space-y-2">
              <Label htmlFor="content">Your Text</Label>
              <Textarea
                id="content"
                value={content}
                onChange={(e) => setContent(e.target.value)}
                placeholder="Enter your text here..."
                className="min-h-[300px] resize-none font-mono"
                disabled={isLoading}
              />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="ttl">Expiration Time (seconds)</Label>
                <Input
                  id="ttl"
                  type="number"
                  value={ttlSeconds}
                  onChange={(e) => setTtlSeconds(e.target.value)}
                  min="1"
                  disabled={isLoading}
                />
                <p className="text-sm text-muted-foreground">
                  Default: 3600 (1 hour)
                </p>
              </div>

              <div className="space-y-2">
                <Label htmlFor="maxViews">Maximum Views</Label>
                <Input
                  id="maxViews"
                  type="number"
                  value={maxViews}
                  onChange={(e) => setMaxViews(e.target.value)}
                  min="1"
                  disabled={isLoading}
                />
                <p className="text-sm text-muted-foreground">
                  Default: 100 views
                </p>
              </div>
            </div>

            <Button type="submit" className="w-full" disabled={isLoading}>
              {isLoading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Creating Paste...
                </>
              ) : (
                "Create Paste"
              )}
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
