import React, { useState, useRef } from "react";
import { api } from "../lib/api";

interface UploadPanelProps {
  onGraphBuilt: () => void;
}

export const UploadPanel: React.FC<UploadPanelProps> = ({ onGraphBuilt }) => {
  const [urls, setUrls] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<"urls" | "file">("urls");
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleBuildGraph = async () => {
    if (activeTab === "urls") {
      if (!urls.trim()) {
        setError("Please enter at least one URL");
        return;
      }

      const urlList = urls
        .split("\n")
        .map((url) => url.trim())
        .filter((url) => url.length > 0);

      if (urlList.length === 0) {
        setError("Please enter at least one valid URL");
        return;
      }

      setIsLoading(true);
      setError(null);

      try {
        await api.ingest(urlList);
        onGraphBuilt();
        setUrls("");
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to build graph");
      } finally {
        setIsLoading(false);
      }
    }
  };

  const handleFileUpload = async (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    const file = event.target.files?.[0];
    if (!file) return;

    // Validate file type
    if (!file.name.endsWith(".txt")) {
      setError("Only TXT files are supported");
      return;
    }

    // Validate file size (5MB)
    if (file.size > 5 * 1024 * 1024) {
      setError("File too large. Maximum size is 5MB");
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      await api.ingestFile(file);
      onGraphBuilt();
      // Clear the file input
      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to process file");
    } finally {
      setIsLoading(false);
    }
  };

  const handleFileButtonClick = () => {
    fileInputRef.current?.click();
  };

  return (
    <div className="bg-gray-800 p-4 rounded-lg">
      <h2 className="text-xl font-bold text-white mb-4">Upload Content</h2>

      {/* Tab Navigation */}
      <div className="flex mb-4 border-b border-gray-600">
        <button
          onClick={() => setActiveTab("urls")}
          className={`px-4 py-2 font-medium transition-colors duration-200 ${
            activeTab === "urls"
              ? "text-blue-400 border-b-2 border-blue-400"
              : "text-gray-400 hover:text-gray-300"
          }`}
        >
          🔗 URLs
        </button>
        <button
          onClick={() => setActiveTab("file")}
          className={`px-4 py-2 font-medium transition-colors duration-200 ${
            activeTab === "file"
              ? "text-blue-400 border-b-2 border-blue-400"
              : "text-gray-400 hover:text-gray-300"
          }`}
        >
          📄 TXT File
        </button>
      </div>

      <div className="space-y-4">
        {activeTab === "urls" ? (
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              URLs (one per line)
            </label>
            <textarea
              value={urls}
              onChange={(e) => setUrls(e.target.value)}
              placeholder="https://example.com&#10;https://another-example.com"
              className="w-full h-32 px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              disabled={isLoading}
            />
          </div>
        ) : (
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Upload TXT File (max 5MB)
            </label>
            <div className="border-2 border-dashed border-gray-600 rounded-md p-6 text-center">
              <p className="text-gray-400 mb-4">
                Click to select a TXT file or drag and drop
              </p>
              <button
                onClick={handleFileButtonClick}
                disabled={isLoading}
                className="bg-green-600 hover:bg-green-700 disabled:bg-gray-600 text-white font-medium py-2 px-4 rounded-md transition-colors duration-200"
              >
                Choose File
              </button>
              <input
                ref={fileInputRef}
                type="file"
                accept=".txt"
                onChange={handleFileUpload}
                className="hidden"
              />
            </div>
          </div>
        )}

        {error && (
          <div className="text-red-400 text-sm bg-red-900/20 p-2 rounded">
            {error}
          </div>
        )}

        {activeTab === "urls" && (
          <button
            onClick={handleBuildGraph}
            disabled={isLoading}
            className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 text-white font-medium py-2 px-4 rounded-md transition-colors duration-200 flex items-center justify-center"
          >
            {isLoading ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                Building Graph...
              </>
            ) : (
              "Build Graph"
            )}
          </button>
        )}
      </div>
    </div>
  );
};
