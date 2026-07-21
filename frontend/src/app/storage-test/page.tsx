"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { ref, uploadBytes, getDownloadURL } from "firebase/storage";
import { Loader2, UploadCloud } from "lucide-react";
import { toast } from "sonner";
import { useAuth } from "@/contexts/auth-context";
import { storage } from "@/lib/firebase";

export default function StorageTestPage() {
  const { user, loading } = useAuth();
  const router = useRouter();
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [downloadUrl, setDownloadUrl] = useState<string | null>(null);

  useEffect(() => {
    if (!loading && !user) {
      router.replace("/auth");
    }
  }, [loading, user, router]);

  if (loading || !user) {
    return null;
  }

  const onUpload = async () => {
    if (!file) return;
    setUploading(true);
    setDownloadUrl(null);
    try {
      const path = `test-uploads/${user.uid}/${Date.now()}-${file.name}`;
      const fileRef = ref(storage, path);
      await uploadBytes(fileRef, file);
      const url = await getDownloadURL(fileRef);
      setDownloadUrl(url);
      toast.success("Upload succeeded.");
    } catch {
      toast.error("Upload failed. Check the console for details.");
    } finally {
      setUploading(false);
    }
  };

  return (
    <main className="flex min-h-screen items-center justify-center bg-[#050b18] px-6 py-16">
      <div className="w-full max-w-[480px] rounded-[28px] border border-white/15 bg-white/10 p-8 shadow-[0_20px_60px_rgba(0,0,0,0.35)] backdrop-blur-2xl">
        <h1
          className="mb-1.5 text-[20px] font-extrabold text-white"
          style={{ fontFamily: "var(--font-sora)" }}
        >
          Phase 1 verification — Storage upload test
        </h1>
        <p className="mb-6 text-[13.5px] leading-relaxed text-white/50">
          Not a product feature. Confirms Firebase Storage upload works from
          the client SDK. Safe to delete once Phase 2 document intake exists.
        </p>

        <input
          type="file"
          onChange={(e) => setFile(e.target.files?.[0] ?? null)}
          disabled={uploading}
          className="mb-4 w-full rounded-2xl border border-white/15 bg-white/5 p-3 text-[13.5px] text-white/80 file:mr-3 file:rounded-lg file:border-0 file:bg-white/10 file:px-3 file:py-1.5 file:text-white"
        />

        <button
          onClick={onUpload}
          disabled={!file || uploading}
          className="inline-flex w-full items-center justify-center gap-2 rounded-2xl bg-gradient-to-r from-[#26D9FF] via-[#3B82F6] to-[#A855F7] py-3 text-[14.5px] font-bold text-white shadow-[0_10px_30px_rgba(59,130,246,0.4)] disabled:cursor-not-allowed disabled:opacity-60"
        >
          {uploading ? (
            <Loader2 size={17} className="animate-spin" />
          ) : (
            <UploadCloud size={17} />
          )}
          Upload test file
        </button>

        {downloadUrl && (
          <div className="mt-6 rounded-2xl border border-white/15 bg-white/5 p-4">
            <p className="mb-2 text-[13px] font-semibold text-white/70">
              Uploaded successfully:
            </p>
            <a
              href={downloadUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="break-all text-[13px] font-semibold text-[#7DD8FF] hover:text-[#A5E6FF]"
            >
              {downloadUrl}
            </a>
            {file?.type.startsWith("image/") && (
              // eslint-disable-next-line @next/next/no-img-element -- runtime Firebase download URL, not a static asset
              <img
                src={downloadUrl}
                alt="Uploaded preview"
                className="mt-4 max-h-[240px] w-full rounded-xl object-contain"
              />
            )}
          </div>
        )}
      </div>
    </main>
  );
}
