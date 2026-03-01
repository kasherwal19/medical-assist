// import { useState, useEffect, useCallback, useRef } from 'react';
// import { Message, APIResponse, StoredDocs, ChatPayload, StructuredContent, SessionHistoryData } from '@/app/result/types';
// import {Files} from '@/components/LeftSidebar'
// import { chatService } from '@/app/result/services/chatService';
// import { API_ENDPOINTS } from '@/data';

// export const useResultData = (sessionId: string | null) => {
//   const [loading, setLoading] = useState(true);
//   const [documents, setDocuments] = useState<Files[]>([]);
//   const [messages, setMessages] = useState<Message[]>([]);
//   const [isSending, setIsSending] = useState(false);
  
//   const messagesRef = useRef<Message[]>([]);

//   const getStorageKey = (sId: string) => `session_history_${sId}`;

//   const updateMessages = (newMessages: Message[]) => {
//     messagesRef.current = newMessages;
//     setMessages(newMessages);
//     if (sessionId) {
//       const key = getStorageKey(sessionId);
//       const existing = sessionStorage.getItem(key);
//       const parsed: SessionHistoryData = existing ? JSON.parse(existing) : { messages: [] };
      
//       const updatedHistory: SessionHistoryData = {
//         ...parsed,
//         messages: newMessages
//       };

//       sessionStorage.setItem(key, JSON.stringify(updatedHistory));
//     }
//   };

//   const updateMessageContent = useCallback((messageId: string, newContent: StructuredContent) => {
//     const updatedMessages = messagesRef.current.map((msg) => 
//       msg.id === messageId ? { ...msg, content: newContent } : msg
//     );
//     updateMessages(updatedMessages);
//   }, [sessionId]);

//   useEffect(() => {
//     const initData = async () => {
//       if (!sessionId) return;
//       setLoading(true);
//       const key = getStorageKey(sessionId);

//       try {
//         const sessionStr = sessionStorage.getItem(key);
//         if (sessionStr) {
//           const parsed = JSON.parse(sessionStr) as SessionHistoryData;
//           if (Array.isArray(parsed.messages)) {
//             messagesRef.current = parsed.messages;
//             setMessages(parsed.messages);
//           }
//         }
//       } catch (e) { console.error("History error", e); }
      
//       setLoading(false);

//       try {
//         const storedDocsStr = sessionStorage.getItem('selectedDocuments');
//         if (storedDocsStr) {
//           const storedDocs = JSON.parse(storedDocsStr);
//           const docsWithUrls = await Promise.all(
//             storedDocs.map(async (doc: StoredDocs) => {
//               const pmcId = typeof doc === "string" ? doc : doc.pmc_id;
//               return {
//                 id: pmcId,
//                 filename: typeof doc === "string" ? pmcId : doc.title || doc.filename,
//                 createdAt: new Date().toLocaleDateString(),
//                 url: await chatService.fetchDocumentViewUrl(pmcId)
//               };
//             })
//           );
//           setDocuments(docsWithUrls);
//         }
//       } catch (e) { console.error("Doc error", e); }
//     };

//     initData();
//   }, [sessionId]); 

//   const handleSendMessage = useCallback(async (query: string) => {
//     if (!query.trim() || !sessionId) return;

//     const tempUserMsg: Message = { 
//         id: Date.now().toString(), 
//         role: 'user', 
//         content: query,
//         createdAt: new Date().toISOString()
//     };
    
//     const currentHistory = [...messagesRef.current, tempUserMsg];
//     updateMessages(currentHistory);
//     setIsSending(true);

//     try {
//       const lastAssistantMsg = currentHistory
//         .slice()
//         .reverse()
//         .find(m => m.role === 'assistant');

//       const lastId = (lastAssistantMsg && typeof lastAssistantMsg.messageId === 'number')
//         ? lastAssistantMsg.messageId 
//         : 0;

//       const nextId = lastId + 1;

//       const key = getStorageKey(sessionId);
//       const sessionStr = sessionStorage.getItem(key);
//       const cachedData = sessionStr ? JSON.parse(sessionStr) as SessionHistoryData : null;
//       const lastContext = cachedData?.lastApiContext || {};

//       const payload: ChatPayload = {
//         session_id: sessionId,
//         user_query: query,
//         images: (lastContext.images as string[]) || [],
//         selectedImageUrl: (lastContext.images?.[0]) || null,
//         selectedImageId: (lastContext.images?.[0]) || null,
//         parameters: lastContext.parameters || {},
//         template: lastContext.template || 'plainhero',
//         message_id: nextId
//       };

//       const response = await fetch(API_ENDPOINTS.CHAT_API, {
//         method: 'POST',
//         headers: { 'Content-Type': 'application/json' },
//         body: JSON.stringify(payload)
//       });
      
//       if (!response.ok) throw new Error('API Failed');
//       const data: APIResponse = await response.json();

//       const usedTemplate = data.selected_template || data.template || 'plainhero';
//       const usedImage = (data.selected_images?.[0]) || (data.images?.[0]);

//       let finalContent: StructuredContent;
//       const responseData = data.response;
      
//       if (responseData?.assistant) {
//           finalContent = responseData.assistant;
//       } else {
//           finalContent = {
//              title: responseData.title || "Generated Content",
//              sections: responseData.sections || []
//           };
//       }

//       const finalMsgId = (typeof data.message_id === 'number') ? data.message_id : nextId;

//       const newAssistantMsg: Message = {
//         id: `${finalMsgId}`,
//         role: 'assistant',
//         content: finalContent,
//         sources: data.sources,
//         messageId: finalMsgId,
//         template: usedTemplate,
//         imageUrl: usedImage,
//         createdAt: new Date().toISOString()
//       };

//       updateMessages([...messagesRef.current, newAssistantMsg]);
      
//       const newHistory: SessionHistoryData = {
//         messages: messagesRef.current,
//         lastApiContext: lastContext
//       };
      
//       sessionStorage.setItem(key, JSON.stringify(newHistory));

//     } catch (err) {
//       console.error('Send error', err);
//     } finally {
//       setIsSending(false);
//     }
//   }, [sessionId]);


//   return {
//     loading,
//     documents,
//     messages,
//     isSending,
//     handleSendMessage,
//     updateMessageContent
//   };
// };

import { useState, useEffect, useCallback, useRef } from 'react';
import { Message, APIResponse, StoredDocs, ChatPayload, StructuredContent, SessionHistoryData } from '@/app/result/types';
import {Files} from '@/components/LeftSidebar'
import { chatService } from '@/app/result/services/chatService';
import { API_ENDPOINTS } from '@/data';

export const useResultData = (sessionId: string | null) => {
  const [loading, setLoading] = useState(true);
  const [documents, setDocuments] = useState<Files[]>([]);
  const [messages, setMessages] = useState<Message[]>([]);
  const [isSending, setIsSending] = useState(false);

  const messagesRef = useRef<Message[]>([]);

  const getStorageKey = (sId: string) => `session_history_${sId}`;

  const updateMessages = (newMessages: Message[]) => {
    messagesRef.current = newMessages;
    setMessages(newMessages);
    if (sessionId) {
      const key = getStorageKey(sessionId);
      const existing = sessionStorage.getItem(key);
      const parsed: SessionHistoryData = existing ? JSON.parse(existing) : { messages: [] };

      const updatedHistory: SessionHistoryData = {
        ...parsed,
        messages: newMessages
      };

      sessionStorage.setItem(key, JSON.stringify(updatedHistory));
    }
  };

  const updateMessageContent = useCallback((messageId: string, newContent: StructuredContent) => {
    const updatedMessages = messagesRef.current.map((msg) => 
      msg.id === messageId ? { ...msg, content: newContent } : msg
    );
    updateMessages(updatedMessages);
  }, [sessionId]);

  useEffect(() => {
    const initData = async () => {
      if (!sessionId) return;
      setLoading(true);
      const key = getStorageKey(sessionId);

      try {
        const sessionStr = sessionStorage.getItem(key);
        if (sessionStr) {
          const parsed = JSON.parse(sessionStr) as SessionHistoryData;
          if (Array.isArray(parsed.messages)) {
            messagesRef.current = parsed.messages;
            setMessages(parsed.messages);
          }
        }
      } catch (e) { console.error("History error", e); }

      setLoading(false);

      try {
        const storedDocsStr = sessionStorage.getItem('selectedDocuments');
        if (storedDocsStr) {
          const storedDocs = JSON.parse(storedDocsStr);
          const docsWithUrls = await Promise.all(
            storedDocs.map(async (doc: StoredDocs) => {
              const pmcId = typeof doc === "string" ? doc : doc.pmc_id;
              return {
                id: pmcId,
                filename: typeof doc === "string" ? pmcId : doc.title || doc.filename,
                createdAt: new Date().toLocaleDateString(),
                url: await chatService.fetchDocumentViewUrl(pmcId)
              };
            })
          );
          setDocuments(docsWithUrls);
        }
      } catch (e) { console.error("Doc error", e); }
    };

    initData();
  }, [sessionId]); 

  const handleSendMessage = useCallback(async (query: string) => {
    if (!query.trim() || !sessionId) return;

    const tempUserMsg: Message = { 
        id: Date.now().toString(), 
        role: 'user', 
        content: query,
        createdAt: new Date().toISOString()
    };

    const currentHistory = [...messagesRef.current, tempUserMsg];
    updateMessages(currentHistory);
    setIsSending(true);

    try {
      const lastAssistantMsg = currentHistory
        .slice()
        .reverse()
        .find(m => m.role === 'assistant');

      const lastId = (lastAssistantMsg && typeof lastAssistantMsg.messageId === 'number')
        ? lastAssistantMsg.messageId 
        : 0;

      const nextId = lastId + 1;

      const key = getStorageKey(sessionId);
      const sessionStr = sessionStorage.getItem(key);
      const cachedData = sessionStr ? JSON.parse(sessionStr) as SessionHistoryData : null;
      const lastContext = cachedData?.lastApiContext || {};

      const payload: ChatPayload = {
        session_id: sessionId,
        user_query: query,
        images: (lastContext.images as string[]) || [],
        selectedImageUrl: (lastContext.images?.[0]) || null,
        selectedImageId: (lastContext.images?.[0]) || null,
        parameters: lastContext.parameters || {},
        template: lastContext.template || 'plainhero',
        message_id: nextId
      };

      const response = await fetch(API_ENDPOINTS.CHAT_API, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      if (!response.ok) throw new Error('API Failed');
      const data: APIResponse = await response.json();

      const usedTemplate = data.selected_template || data.template || 'plainhero';
      const usedImage = (data.selected_images?.[0]) || (data.images?.[0]);

      const finalMsgId = (typeof data.message_id === 'number') ? data.message_id : nextId;

      let newAssistantMsg: Message;

      // Check if this is a Q&A response (plain text answer)
      if (data.qa_answer) {
        newAssistantMsg = {
          id: `${finalMsgId}`,
          role: 'assistant',
          content: data.qa_answer,
          sources: data.sources,
          messageId: finalMsgId,
          createdAt: new Date().toISOString()
        };
      } else {
        let finalContent: StructuredContent;
        const responseData = data.response;

        if (responseData?.assistant) {
            finalContent = responseData.assistant;
        } else {
            finalContent = {
               title: responseData.title || "Generated Content",
               sections: responseData.sections || []
            };
        }

        newAssistantMsg = {
          id: `${finalMsgId}`,
          role: 'assistant',
          content: finalContent,
          sources: data.sources,
          messageId: finalMsgId,
          template: usedTemplate,
          imageUrl: usedImage,
          createdAt: new Date().toISOString()
        };
      }

      updateMessages([...messagesRef.current, newAssistantMsg]);

      const newHistory: SessionHistoryData = {
        messages: messagesRef.current,
        lastApiContext: lastContext
      };

      sessionStorage.setItem(key, JSON.stringify(newHistory));

    } catch (err) {
      console.error('Send error', err);
    } finally {
      setIsSending(false);
    }
  }, [sessionId]);


  return {
    loading,
    documents,
    messages,
    isSending,
    handleSendMessage,
    updateMessageContent
  };
};