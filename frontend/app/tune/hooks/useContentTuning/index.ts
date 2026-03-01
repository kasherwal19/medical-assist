import { useState, useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { ImageItem } from '@/app/tune/types/index';
import { APIResponse, Message, StructuredContent, SessionHistoryData } from '@/app/result/types/index';
import { tuningService } from '@/app/tune/services/tuningService';

export function useContentTuning() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const sessionId = searchParams.get('session_id');
  const [currentStep, setCurrentStep] = useState(1);
  const [isGenerating, setIsGenerating] = useState(false);
  const [showOptional, setShowOptional] = useState(false);
  const [includeImages, setIncludeImages] = useState(false);
  const [selections, setSelections] = useState<Record<string, string[]>>({});
  const [isLoadingImages, setIsLoadingImages] = useState(false);
  const [selectedImageId, setSelectedImageId] = useState<string | null>(null);
  const [allImages, setAllImages] = useState<ImageItem[]>([]);
  const [selectedTemplate, setSelectedTemplate] = useState<string | null>(null);

  useEffect(() => {
    const loadImages = async () => {
      setIsLoadingImages(true);
      try {
        const images = await tuningService.fetchImages();
        setAllImages(images);
      } catch (err) {
        console.error(err);
      } finally {
        setIsLoadingImages(false);
      }
    };
    loadImages();
  }, []);

  const handleBack = () => {
    if (currentStep === 1) {
      router.back();
    } else if (currentStep === 2) {
      setCurrentStep(1);
    } else if (currentStep === 3) {
      setCurrentStep(includeImages ? 2 : 1);
    }
  };

  const performGeneration = async () => {
    if(isGenerating) return;
    if (!sessionId || !selectedTemplate) return;
    setIsGenerating(true);
    
    try {
      const apiResponse: APIResponse = await tuningService.generateContent({
        session_id: sessionId,
        parameters: selections,
        selectedImageId,
        selectedTemplate
      });

      if (typeof window !== 'undefined') {
        const key = `session_history_${sessionId}`;
        const existingStr = sessionStorage.getItem(key);
        let existingMessages: Message[] = [];
        
        if (existingStr) {
           try {
             const parsed = JSON.parse(existingStr) as SessionHistoryData;
             if (Array.isArray(parsed.messages)) existingMessages = parsed.messages;
           } catch(e) { console.error("Error parsing history", e); }
        }
        
        const lastAssistantMsg = [...existingMessages].findLast(m => m.role === 'assistant');
        
        const lastId = (lastAssistantMsg && typeof lastAssistantMsg.messageId === 'number') 
          ? lastAssistantMsg.messageId 
          : 0;
          
        const nextId = lastId + 1;

        let finalContent: StructuredContent;
        const responseData = apiResponse.response;

        if (responseData.assistant) {
            finalContent = responseData.assistant;
        } else {
            finalContent = {
                title: responseData.title || "Generated Content",
                sections: responseData.sections || []
            };
        }

        let finalImageUrl: string | undefined = undefined;
        if (selectedImageId) {
            if (/^https?:\/\//i.test(selectedImageId)) {
                finalImageUrl = selectedImageId;
            } else {
                const found = allImages.find(img => img.id === selectedImageId);
                if (found) finalImageUrl = found.src || found.azure_url;
            }
        }

        const newMessage: Message = {
            id: `${nextId}`,
            role: 'assistant',
            content: finalContent,
            sources: apiResponse.sources,
            messageId: nextId,
            template: selectedTemplate,
            imageUrl: finalImageUrl,
            createdAt: new Date().toISOString()
        };

        const updatedMessages = [...existingMessages, newMessage];
        
        const historyData: SessionHistoryData = {
          messages: updatedMessages,
          lastApiContext: {
             parameters: selections,
             template: selectedTemplate,
             images: includeImages ? [selectedImageId] : []
          }
        };

        sessionStorage.setItem(key, JSON.stringify(historyData));
      }

      router.push(`/result?session_id=${sessionId}`);

    } catch (error) {
      console.error('Error calling generate API', error);
      setIsGenerating(false);
    }
  };

  const handleNext = () => {
    if (currentStep === 1) {
      setCurrentStep(includeImages ? 2 : 3);
    } else if (currentStep === 2) {
      setCurrentStep(3);
    } else if (currentStep === 3) {
      performGeneration();
    }
  };

  return {
    sessionId,
    currentStep,
    isGenerating,
    showOptional, setShowOptional,
    includeImages, setIncludeImages,
    selections, setSelections,
    isLoadingImages,
    selectedImageId, setSelectedImageId,
    allImages,
    selectedTemplate, setSelectedTemplate,
    handleBack,
    handleNext
  };
}