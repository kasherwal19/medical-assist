export const templates = [
  {
    id: 'hero',
    label: 'Hero Banner Layout',
    withImage: true,
    Preview: () => (
      <div className="w-full aspect-[3/4] bg-[#F4F4F4] p-4 flex flex-col gap-4 border border-dashed border-gray-300">
        <div className="w-full h-1/3 bg-[#D9D9D9] flex items-center justify-center text-gray-500 font-bold text-xs tracking-widest relative">
          IMAGE
        </div>
        <div className="space-y-2">
          <div className="h-1.5 bg-gray-300 w-1/3 rounded"></div>
          <div className="space-y-1.5 mt-4">
             {[...Array(6)].map((_, i) => <div key={i} className={`h-1.5 bg-gray-300 rounded ${i === 5 ? 'w-2/3' : 'w-full'}`}></div>)}
          </div>
          <div className="space-y-1.5 mt-4">
             {[...Array(4)].map((_, i) => <div key={i} className={`h-1.5 bg-gray-300 rounded ${i === 3 ? 'w-1/2' : 'w-full'}`}></div>)}
          </div>
        </div>
      </div>
    )
  },
  {
    id: 'dual',
    label: 'Dual Column Layout',
    withImage: true,
    Preview: () => (
      <div className="w-full aspect-[3/4] bg-[#F4F4F4] p-4 grid grid-cols-2 gap-3 border border-dashed border-gray-300 justify-between">
        <div className="flex flex-col gap-2">
          <div className="w-full aspect-square bg-[#D9D9D9] flex items-center justify-center text-[10px] text-gray-500 font-bold relative">
            IMAGE
          </div>
          <div className="space-y-1.5">
            <div className="h-1.5 bg-gray-300 w-3/4 rounded mb-2"></div>
            {[...Array(10)].map((_, i) => (
              <div key={i} className="h-1.5 bg-gray-300 rounded w-full"></div>
            ))}
          </div>
        </div>
        <div className="flex flex-col gap-2">
          <div className="space-y-1.5 mt-6">
            <div className="h-1.5 bg-gray-300 w-2/3 rounded mb-2"></div>
            {[...Array(8)].map((_, i) => (
              <div key={i} className="h-1.5 bg-gray-300 rounded w-full"></div>
            ))}
          </div>
        </div>
      </div>
    )
  },
  {
    id: 'embedded',
    label: 'Embedded Image Layout',
    withImage: true,
    Preview: () => (
      <div className="w-full aspect-[3/4] bg-[#F4F4F4] p-4 border border-dashed border-gray-300 relative">
        <div className="flex flex-col gap-2">
           <div className="h-1.5 bg-gray-300 w-full rounded"></div>
           <div className="h-1.5 bg-gray-300 w-full rounded"></div>
           <div className="h-1.5 bg-gray-300 w-3/4 rounded mb-2"></div>
           <div className="flex gap-3">
              <div className="w-1/2 aspect-square bg-[#D9D9D9] flex items-center justify-center text-xs text-gray-500 font-bold shrink-0">IMAGE</div>
              <div className="w-full space-y-1.5 pt-1">
                 {[...Array(6)].map((_, i) => <div key={i} className="h-1.5 bg-gray-300 rounded w-full"></div>)}
              </div>
           </div>
           <div className="space-y-1.5 mt-1">
               {[...Array(5)].map((_, i) => <div key={i} className="h-1.5 bg-gray-300 rounded w-full"></div>)}
           </div>
        </div>
      </div>
    )
  },
  {
    id: 'plainhero',
    label: 'Hero Layout',
    withImage: false,
    Preview: () => (
      <div className="w-full aspect-[3/4] bg-[#F4F4F4] p-4 flex flex-col gap-4 border border-dashed border-gray-300">
        <div className="space-y-2">
          <div className="h-1.5 bg-gray-300 w-1/2 rounded"></div>

          <div className="space-y-1.5 mt-4">
            {[...Array(8)].map((_, i) => (
              <div
                key={i}
                className={`h-1.5 bg-gray-300 rounded ${
                  i === 7 ? 'w-2/3' : 'w-full'
                }`}
              />
            ))}
          </div>

          <div className="space-y-1.5 mt-4">
            {[...Array(5)].map((_, i) => (
              <div
                key={i}
                className={`h-1.5 bg-gray-300 rounded ${
                  i === 4 ? 'w-1/2' : 'w-full'
                }`}
              />
            ))}
          </div>
        </div>
      </div>
    )
  },
  {
    id: 'plaindual',
    label: 'Dual Column Layout',
    withImage: false,
    Preview: () => (
      <div className="w-full aspect-[3/4] bg-[#F4F4F4] p-4 grid grid-cols-2 gap-4 border border-dashed border-gray-300">
        <div className="space-y-1.5">
          <div className="h-1.5 bg-gray-300 w-3/4 rounded mb-2"></div>
          {[...Array(10)].map((_, i) => (
            <div key={i} className="h-1.5 bg-gray-300 rounded w-full"></div>
          ))}
        </div>

        <div className="space-y-1.5">
          <div className="h-1.5 bg-gray-300 w-2/3 rounded mb-2"></div>
          {[...Array(8)].map((_, i) => (
            <div key={i} className="h-1.5 bg-gray-300 rounded w-full"></div>
          ))}
        </div>
      </div>
    )
    }
];