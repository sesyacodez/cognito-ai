import React from "react";

export default function ErrorState({ message = "Something went wrong." }: { message?: string }) {
  return (
    <div className="w-full py-8 px-4 bg-red-900/10 border border-red-600/20 rounded-lg text-red-300">
      <p className="text-sm">{message}</p>
    </div>
  );
}
