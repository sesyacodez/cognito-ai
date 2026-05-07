import React from "react";

export default function LoadingState({ message = "Loading..." }: { message?: string }) {
  return (
    <div className="w-full py-10 flex flex-col items-center justify-center text-center">
      <div className="w-10 h-10 border-4 border-gray-700 border-t-blue-500 rounded-full animate-spin mb-4" role="status" aria-label="loading" />
      <p className="text-sm text-gray-400">{message}</p>
    </div>
  );
}
