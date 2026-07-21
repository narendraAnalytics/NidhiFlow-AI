import { ref, uploadBytes, getDownloadURL } from "firebase/storage";
import { storage } from "@/lib/firebase";
import type { DocumentType } from "@/types/loan";

function slugifyDocumentType(documentType: DocumentType): string {
  return documentType.toLowerCase().replace(/\s+/g, "-");
}

export async function uploadLoanDocument(
  loanApplicationId: string,
  documentType: DocumentType,
  file: File,
): Promise<string> {
  const path = `loan-documents/${loanApplicationId}/${slugifyDocumentType(documentType)}/${Date.now()}-${file.name}`;
  const fileRef = ref(storage, path);
  await uploadBytes(fileRef, file);
  return getDownloadURL(fileRef);
}
