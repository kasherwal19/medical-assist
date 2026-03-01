import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Article } from '@/app/search/types';
import { searchService } from '@/app/search/services/searchService';

const isBrowser = typeof window !== 'undefined';

export function useDocSelection(results: Article[], sessionId: string | null) {
  const router = useRouter();
  const [selectedItems, setSelectedItems] = useState<Set<string>>(new Set());
  const [isProcessing, setIsProcessing] = useState(false);

  const toggleSelection = (id: string) => {
    const updated = new Set(selectedItems);
    updated.has(id) ? updated.delete(id) : updated.add(id);
    setSelectedItems(updated);
  };

  const clearSelection = () => setSelectedItems(new Set());

  const handleProceed = async () => {
    if (selectedItems.size === 0 || !sessionId) return;

    try {
      setIsProcessing(true);
      const selectedDocs = results.filter((doc) => selectedItems.has(doc.pmc_id));
      
      if (isBrowser) {
        sessionStorage.setItem('selectedDocuments', JSON.stringify(selectedDocs));
      }

      await searchService.triggerProcessing(sessionId, Array.from(selectedItems));
      router.push(`/tune?session_id=${sessionId}`); 
    } catch (error) {
      console.error('Error sending documents for processing:', error);
    } finally {
      setIsProcessing(false);
    }
  };

  return {
    selectedItems,
    isProcessing,
    toggleSelection,
    clearSelection,
    handleProceed
  };
}