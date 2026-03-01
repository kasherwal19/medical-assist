import Image from 'next/image';

interface VersionControlsProps {
  onEdit: () => void;
  onDownload: () => void;
}

export const VersionControls = ({ onEdit, onDownload }: VersionControlsProps) => {
  return (
    <div className="w-40 flex flex-col gap-3 shrink-0 sticky top-0 h-fit">
      <button
        className="flex items-center gap-3 px-4 py-2.5 border border-slate-200 bg-white text-slate-700 rounded-xl text-sm font-medium hover:bg-slate-50 hover:text-accent1 transition-all shadow-sm hover:shadow-md cursor-pointer group"
        onClick={onEdit}
      >
        <div className="w-7 h-7 rounded-full bg-slate-100 flex items-center justify-center group-hover:bg-blue-50 transition-colors">
          <Image src="/icons/edit.svg" alt="Edit" width={14} height={14} className="opacity-70 group-hover:opacity-100" />
        </div>
        Edit Draft
      </button>
      <button
        className="flex items-center gap-3 px-4 py-2.5 border border-slate-200 bg-white text-slate-700 rounded-xl text-sm font-medium hover:bg-slate-50 hover:text-accent1 transition-all shadow-sm hover:shadow-md cursor-pointer group"
        onClick={onDownload}
      >
        <div className="w-7 h-7 rounded-full bg-slate-100 flex items-center justify-center group-hover:bg-blue-50 transition-colors">
          <Image src="/icons/download.svg" alt="Download" width={14} height={14} className="opacity-70 group-hover:opacity-100" />
        </div>
        Download
      </button>
    </div>
  );
};