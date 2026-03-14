import { useEffect, useState } from "react";
import { useParams, Link } from "react-router";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../components/ui/card";
import { Button } from "../components/ui/button";
import { Skeleton } from "../components/ui/skeleton";
import { Alert, AlertDescription, AlertTitle } from "../components/ui/alert";
import { getPaste, GetPasteResponse, ErrorResponse } from "../utils/api";
import { Clock, Eye, AlertCircle, PlusCircle } from "lucide-react";

export default function ViewPaste() {
  const { id } = useParams<{ id: string }>();
  const [paste, setPaste] = useState<GetPasteResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isExpired, setIsExpired] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchPaste() {
      if (!id) return;

      setIsLoading(true);
      setError(null);
      setIsExpired(false);

      try {
        const response = await getPaste(id);

        // Check if response is an error response
        if ("detail" in response) {
          const errorResponse = response as ErrorResponse;
          if (errorResponse.detail === "Paste not found") {
            setIsExpired(true);
          } else {
            setError(errorResponse.detail);
          }
        } else {
          setPaste(response as GetPasteResponse);
        }
      } catch (err) {
        setError("Failed to load paste. Please try again.");
        console.error(err);
      } finally {
        setIsLoading(false);
      }
    }

    fetchPaste();
  }, [id]);

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 p-4 flex items-center justify-center">
        <Card className="w-full max-w-4xl shadow-lg">
          <CardHeader>
            <Skeleton className="h-8 w-48" />
            <Skeleton className="h-4 w-64" />
          </CardHeader>
          <CardContent className="space-y-4">
            <Skeleton className="h-64 w-full" />
            <div className="flex gap-4">
              <Skeleton className="h-4 w-32" />
              <Skeleton className="h-4 w-32" />
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (isExpired) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-red-50 to-orange-100 p-4 flex items-center justify-center">
        <Card className="w-full max-w-2xl shadow-lg">
          <CardHeader>
            <div className="flex items-center gap-2">
              <AlertCircle className="h-6 w-6 text-red-500" />
              <CardTitle className="text-2xl">Paste Expired</CardTitle>
            </div>
            <CardDescription>
              This paste is no longer available
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <Alert variant="destructive">
              <AlertCircle className="h-4 w-4" />
              <AlertTitle>Data Has Expired</AlertTitle>
              <AlertDescription>
                This paste has either expired due to the time limit, reached its maximum
                view count, or was never created. The content is no longer accessible.
              </AlertDescription>
            </Alert>

            <Button asChild className="w-full">
              <Link to="/">
                <PlusCircle className="mr-2 h-4 w-4" />
                Create a New Paste
              </Link>
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-red-50 to-orange-100 p-4 flex items-center justify-center">
        <Card className="w-full max-w-2xl shadow-lg">
          <CardHeader>
            <div className="flex items-center gap-2">
              <AlertCircle className="h-6 w-6 text-red-500" />
              <CardTitle className="text-2xl">Error</CardTitle>
            </div>
          </CardHeader>
          <CardContent className="space-y-6">
            <Alert variant="destructive">
              <AlertCircle className="h-4 w-4" />
              <AlertTitle>Error Loading Paste</AlertTitle>
              <AlertDescription>{error}</AlertDescription>
            </Alert>

            <Button asChild className="w-full">
              <Link to="/">
                <PlusCircle className="mr-2 h-4 w-4" />
                Create a New Paste
              </Link>
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (!paste) {
    return null;
  }

  const expiresDate = new Date(paste.expires_at);

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 to-indigo-100 p-4 flex items-center justify-center">
      <Card className="w-full max-w-4xl shadow-lg">
        <CardHeader>
          <CardTitle className="text-2xl">Paste {id}</CardTitle>
          <CardDescription className="flex flex-wrap gap-4 pt-2">
            <span className="flex items-center gap-1">
              <Eye className="h-4 w-4" />
              {paste.remaining_views} views remaining
            </span>
            <span className="flex items-center gap-1">
              <Clock className="h-4 w-4" />
              Expires: {expiresDate.toLocaleString()}
            </span>
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="bg-gray-50 border border-gray-200 rounded-lg p-4 max-h-[500px] overflow-y-auto">
            <pre className="whitespace-pre-wrap break-words font-mono text-sm">
              {paste.content}
            </pre>
          </div>

          <Button asChild variant="outline" className="w-full">
            <Link to="/">Create Your Own Paste</Link>
          </Button>
        </CardContent>
      </Card>
    </div>
  );
}
