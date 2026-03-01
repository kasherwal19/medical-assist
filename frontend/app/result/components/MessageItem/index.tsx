// import { useRef, useState } from "react";
// import { Message, StructuredContent } from "@/app/result/types";
// import { TemplateRenderer } from "@/app/result/components/TemplateRenderer";
// import { VersionControls } from "@/app/result/components/VersionControl";
// import { ContentEditor } from "@/app/result/components/ContentEditor";

// export const MessageItem = ({
//   msg,
//   onUpdate,
//   onDownload,
// }: {
//   msg: Message,
//   onUpdate: (newContent: StructuredContent) => void,
//   onDownload: (id: string, element: HTMLElement) => void,
//   onEdit?: () => void;
// }) => {
//   const isUser = msg.role === 'user';
//   const contentRef = useRef<HTMLDivElement | null>(null);
//   const [isEditing, setIsEditing] = useState(false);

//   const handleDownload = () => {
//     if (contentRef.current) {
//       onDownload(msg.id, contentRef.current);
//     }
//   };


//   const handleEditClick = () => {
//     setIsEditing(true);
//   };

//   const handleSave = (newContent: StructuredContent) => {
//     onUpdate(newContent);
//     setIsEditing(false);
//   };


//   if (isUser) {
//     return (
//       <div className="flex justify-end gap-6 animate-fadeIn">
//         <div className="max-w-[80%] bg-white text-slate-700 rounded-2xl rounded-tr-sm p-4 px-6 shadow-sm border border-slate-200 whitespace-pre-wrap">
//           <span className="text-slate-900 font-medium mb-1 block">You</span>
//           {msg.content as string}
//         </div>
//       </div>
//     );
//   }

//   return (
//     <div className="flex gap-4 animate-fadeIn items-start w-full">
//       <div className="w-10 h-10 rounded-full bg-white border border-slate-200 flex-shrink-0 flex items-center justify-center shadow-sm mt-2">
//         <span className="text-lg font-bold text-transparent bg-clip-text bg-gradient-to-r from-accent1 to-accent2">E</span>
//       </div>

//       <div className="flex-1 min-w-0" ref={contentRef}>
//         {isEditing && typeof msg.content !== 'string' ? (
//           <ContentEditor
//             content={msg.content as StructuredContent}
//             onSave={handleSave}
//             onCancel={() => setIsEditing(false)}
//           />
//         ) : (
//           <div className="bg-white rounded-2xl rounded-tl-none shadow-sm border border-slate-200 overflow-hidden relative">
//             <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-accent1 to-accent2 pointer-events-none z-10" />
//             <TemplateRenderer
//               content={msg.content}
//               template={msg.template || 'plainhero'}
//               imageUrl={msg.imageUrl}
//             />
//           </div>
//         )}
//       </div>

//       {!isEditing && (
//         <div className="shrink-0 pt-2">
//           <VersionControls
//             onEdit={handleEditClick}
//             onDownload={handleDownload}
//           />
//         </div>
//       )}
//     </div>
//   );
// };



import { useRef, useState } from "react";
import { Message, StructuredContent } from "@/app/result/types";
import { TemplateRenderer } from "@/app/result/components/TemplateRenderer";
import { VersionControls } from "@/app/result/components/VersionControl";
import { ContentEditor } from "@/app/result/components/ContentEditor";

export const MessageItem = ({ 
  msg, 
  onUpdate,
  onDownload, 
}: { 
  msg: Message, 
  onUpdate: (newContent: StructuredContent) => void,
  onDownload: (id: string, element: HTMLElement) => void,
  onEdit?: () => void;
}) => {
  const isUser = msg.role === 'user';
  const contentRef = useRef<HTMLDivElement | null>(null);
  const [isEditing, setIsEditing] = useState(false);

  const handleDownload = () => {
    if (contentRef.current) {
      onDownload(msg.id, contentRef.current);
    }
  };


  const handleEditClick = () => {
      setIsEditing(true);
  };

  const handleSave = (newContent: StructuredContent) => {
      onUpdate(newContent);
      setIsEditing(false);
  };


  if (isUser) {
    return (
      <div className="flex justify-end gap-6 animate-fadeIn">
        <div className="max-w-[80%] bg-gray-100 text-gray-800 rounded-2xl rounded-tr-sm p-4 px-6 shadow-sm border border-gray-200 whitespace-pre-wrap">
          {msg.content as string}
        </div>
      </div>
    );
  }

  // Q&A plain text response — render as a simple chat bubble without edit/download controls
  if (typeof msg.content === 'string') {
    return (
      <div className="flex gap-4 animate-fadeIn items-start w-full">
        <div className="flex-1 min-w-0">
          <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-6">
            <div className="text-gray-800 leading-relaxed whitespace-pre-wrap">
              {msg.content}
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="flex gap-4 animate-fadeIn items-start w-full">
      <div className="flex-1 min-w-0" ref={contentRef}>
        {isEditing && typeof msg.content !== 'string' ? (
             <ContentEditor 
                content={msg.content as StructuredContent} 
                onSave={handleSave}
                onCancel={() => setIsEditing(false)} 
             />
        ) : (
            <div className="bg-fill rounded-xl shadow-sm">
                <TemplateRenderer
                    content={msg.content}
                    template={msg.template || 'plainhero'}
                    imageUrl={msg.imageUrl}
                />
            </div>
        )}
      </div>

      {!isEditing && (
        <div className="shrink-0 pt-2">
            <VersionControls
            onEdit={handleEditClick}
            onDownload={handleDownload}
            />
        </div>
      )}
    </div>
  );
};