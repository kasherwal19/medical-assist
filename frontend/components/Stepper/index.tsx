import React from 'react';
import Image from 'next/image';

export default function Stepper({ currentStep }: { currentStep: number }) {
  const steps = [
    { id: 1, label: 'Select Parameters' },
    { id: 2, label: 'Add Image' },
    { id: 3, label: 'Choose Template' },
  ];

  return (
    <div className="w-full bg-white p-8 rounded-2xl mb-8 relative border border-slate-200 shadow-sm">
      <div className="relative w-full max-w-4xl mx-auto">
        <div className="flex items-start justify-between w-full relative before:absolute before:top-5 before:left-[10%] before:w-[80%] before:h-0.5 before:bg-slate-200 before:-z-10">
          {steps.map((step) => {
            const isActive = currentStep === step.id;
            const isCompleted = currentStep > step.id;

            return (
              <div key={step.id} className="flex flex-col items-center relative z-10 w-1/3">
                <div
                  className={`w-10 h-10 rounded-full flex items-center justify-center text-sm font-semibold transition-all duration-300 ${isActive
                    ? "bg-gradient-to-br from-accent1 to-accent2 text-white shadow-md border-2 border-white scale-110"
                    : isCompleted
                      ? "bg-accent1 text-white border-2 border-white shadow-sm"
                      : "bg-slate-50 text-slate-400 border-2 border-slate-200"
                    }`}
                >
                  {isCompleted ? (
                    <Image src="/icons/check.svg" alt="Completed" width={16} height={16} className="invert brightness-0" />
                  ) : (
                    step.id
                  )}
                </div>
                <span
                  className={`mt-4 text-sm font-medium transition-colors ${isActive ? "text-accent1 font-semibold" : isCompleted ? "text-slate-700" : "text-slate-400"
                    }`}
                >
                  {step.label}
                </span>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}