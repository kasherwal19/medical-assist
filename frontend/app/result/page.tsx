'use client';

import { useRef, useEffect, Suspense, useCallback } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import Header from '@/components/Header';
import LeftSidebar from '@/components/LeftSidebar';
import { ChatInput } from '@/app/result/components/ChatInput';
import { useResultData } from '@/app/result/hooks/useResultData';
import { MessageItem } from '@/app/result/components/MessageItem';

function ResultContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const sessionId = searchParams.get('session_id');

  const {
    loading,
    documents,
    messages,
    isSending,
    handleSendMessage,
    updateMessageContent
  } = useResultData(sessionId);

  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, isSending]);

  const handleChangeParameters = useCallback(() => {
    router.push(`/tune?session_id=${sessionId}`);
  }, [router, sessionId]);

  const onDownloadClick = useCallback(async (msgId: string, element: HTMLElement) => {
    try {
      const html2canvas = (await import('html2canvas-pro')).default;
      const jsPDF = (await import('jspdf')).default;
      const canvas = await html2canvas(element, {
        scale: 2,
        useCORS: true,
        logging: false,
        backgroundColor: '#ffffff',
      });

      const imgData = canvas.toDataURL('image/jpeg', 0.98);
      const imgWidth = canvas.width;
      const imgHeight = canvas.height;
      const pxToMm = 0.264583;
      const pdfWidth = imgWidth * pxToMm;
      const pdfHeight = imgHeight * pxToMm;
      const pdf = new jsPDF({
        orientation: pdfHeight > pdfWidth ? 'p' : 'l',
        unit: 'mm',
        format: [pdfWidth, pdfHeight]
      });

      pdf.addImage(imgData, 'JPEG', 0, 0, pdfWidth, pdfHeight);
      pdf.save(`Draft${msgId}.pdf`);

    } catch (error) {
      console.error("PDF Generation failed:", error);
    }
  }, []);


  return (
    <div className="h-screen bg-slate-50 flex flex-col overflow-hidden text-body font-sans relative">
      {/* Background Gradient Mesh */}
      <div className="absolute top-[-20%] left-[-10%] w-[50%] h-[50%] bg-blue-100/40 rounded-full blur-[120px] pointer-events-none" />
      <div className="absolute bottom-[-20%] right-[-10%] w-[50%] h-[50%] bg-teal-100/40 rounded-full blur-[120px] pointer-events-none" />

      <div className="relative z-10">
        <Header />
      </div>

      <main className="flex-1 flex overflow-hidden gap-6 p-6 pt-2 relative z-10 animate-fadeIn">

        <div className="w-[400px] bg-white rounded-2xl shadow-sm border border-slate-200 flex flex-col shrink-0 overflow-hidden h-full">
          {loading ? (
            <div className="flex items-center justify-center h-full">
              <span className="text-sm text-slate-500 animate-pulse">Loading documents...</span>
            </div>
          ) : (
            <LeftSidebar files={documents} sessionId={sessionId || 'demo'} />
          )}
        </div>

        <div className="flex-1 flex flex-col relative overflow-hidden h-full">

          <div className="flex-1 overflow-y-auto custom-scrollbar pb-6 pr-2" ref={scrollRef}>
            <div className="max-w-7xl mx-auto flex flex-col gap-8">

              {messages.map((msg) => (
                <MessageItem
                  key={msg.id}
                  msg={msg}
                  onUpdate={(newContent) => updateMessageContent(msg.id, newContent)}
                  onDownload={onDownloadClick}
                />
              ))}

              {isSending && (
                <div className="flex gap-6 animate-pulse mt-4">
                  <div className="w-10 h-10 rounded-full bg-white border border-slate-200 flex-shrink-0 flex items-center justify-center shadow-sm">
                    <span className="text-lg font-bold text-transparent bg-clip-text bg-gradient-to-r from-accent1 to-accent2">E</span>
                  </div>

                  <div className="flex-1 bg-white border border-slate-200 rounded-xl rounded-tl-none p-6 shadow-sm flex items-center">
                    <div className="flex space-x-2">
                      <div className="w-2.5 h-2.5 bg-accent1 rounded-full animate-bounce shadow-sm" style={{ animationDelay: '0ms' }}></div>
                      <div className="w-2.5 h-2.5 bg-accent1 rounded-full animate-bounce shadow-sm" style={{ animationDelay: '150ms' }}></div>
                      <div className="w-2.5 h-2.5 bg-accent1 rounded-full animate-bounce shadow-sm" style={{ animationDelay: '300ms' }}></div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>

          <ChatInput
            onSend={handleSendMessage}
            isSending={isSending}
            onChangeParameters={handleChangeParameters}
          />

        </div>
      </main>
    </div>
  );
}

export default function ResultPage() {
  return (
    <Suspense fallback={<div className="h-screen w-full flex items-center justify-center bg-slate-50 text-slate-500">Loading Result...</div>}>
      <ResultContent />
    </Suspense>
  );
}