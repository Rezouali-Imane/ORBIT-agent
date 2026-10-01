import { v4 as uuidv4 } from "uuid";
import { ReactNode, useEffect, useRef } from "react";
import { motion } from "framer-motion";
import { cn } from "@/lib/utils";
import { useStreamContext } from "@/providers/Stream";
import { useState, FormEvent } from "react";
import { Button } from "../ui/button";
import { Checkpoint, Message } from "@langchain/langgraph-sdk";
import { AssistantMessage, AssistantMessageLoading } from "./messages/ai";
import { HumanMessage } from "./messages/human";
import {
  DO_NOT_RENDER_ID_PREFIX,
  ensureToolCallsHaveResponses,
} from "@/lib/ensure-tool-responses";
import { TooltipIconButton } from "./tooltip-icon-button";
import {
  ArrowDown,
  Activity,
  LoaderCircle,
  SquarePen,
  X,
} from "lucide-react";
import { useQueryState } from "nuqs";
import { StickToBottom, useStickToBottomContext } from "use-stick-to-bottom";
import { toast } from "sonner";
import { GitHubSVG } from "../icons/github";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "../ui/tooltip";

const specialistLabels: Record<string, { label: string; detail: string }> = {
  librarian: { label: "Librarian", detail: "Searching your documents" },
  researcher: { label: "Researcher", detail: "Gathering live sources" },
  checker: { label: "Checker", detail: "Auditing the draft" },
  create_roadmap: { label: "Roadmap studio", detail: "Drawing the plan" },
};

function getActivity(messages: Message[], isLoading: boolean) {
  const calls = messages.flatMap((message) => {
    if (message.type !== "ai" || !("tool_calls" in message) || !Array.isArray(message.tool_calls)) {
      return [];
    }
    return message.tool_calls.filter((call) => specialistLabels[call.name]);
  });
  const latest = calls[calls.length - 1];
  const active = latest && isLoading ? latest.name : undefined;
  const log = calls.slice(-5).reverse().map((call) => ({
    name: call.name,
    label: specialistLabels[call.name]?.label ?? call.name,
    detail: specialistLabels[call.name]?.detail ?? "Working on your request",
  }));
  return { active, log };
}

function ActivityPanel({
  messages,
  isLoading,
  open,
  onClose,
}: {
  messages: Message[];
  isLoading: boolean;
  open: boolean;
  onClose: () => void;
}) {
  const { active, log } = getActivity(messages, isLoading);
  return (
    <aside className={cn("orbit-activity-panel", open && "orbit-activity-panel--open")}>
      <div className="orbit-activity__header"><div><span className="orbit-kicker">Workspace</span><h2>Activity</h2></div><button className="orbit-icon-button orbit-mobile-only" onClick={onClose} aria-label="Close activity"><X size={17} /></button></div>
      <div className="orbit-specialist-status">{Object.entries(specialistLabels).map(([key, specialist]) => <div className={cn("orbit-specialist-status__item", active === key && "is-working")} key={key}><span><strong>{specialist.label}</strong><small>{active === key ? "Working now" : "Ready"}</small></span><i /></div>)}</div>
      <div className="orbit-activity__log"><div className="orbit-sidebar__section-title">Recent steps</div>{log.length ? log.map((step, index) => <div className="orbit-activity__log-item" key={`${step.name}-${index}`}><span>{String(index + 1).padStart(2, "0")}</span><p>{step.label} <small>{step.detail}</small></p></div>) : <p className="orbit-muted">Activity will appear here as Orbit works.</p>}</div>
    </aside>
  );
}

function StickyToBottomContent(props: {
  content: ReactNode;
  footer?: ReactNode;
  className?: string;
  contentClassName?: string;
}) {
  const context = useStickToBottomContext();
  return (
    <div
      ref={context.scrollRef}
      style={{ width: "100%", height: "100%" }}
      className={props.className}
    >
      <div ref={context.contentRef} className={props.contentClassName}>
        {props.content}
      </div>

      {props.footer}
    </div>
  );
}

function ScrollToBottom(props: { className?: string }) {
  const { isAtBottom, scrollToBottom } = useStickToBottomContext();

  if (isAtBottom) return null;
  return (
    <Button
      variant="outline"
      className={props.className}
      onClick={() => scrollToBottom()}
    >
      <ArrowDown className="w-4 h-4" />
      <span>Scroll to bottom</span>
    </Button>
  );
}

function OpenGitHubRepo() {
  return (
    <TooltipProvider>
      <Tooltip>
        <TooltipTrigger asChild>
          <a
            href="https://github.com/langchain-ai/agent-chat-ui"
            target="_blank"
            className="flex items-center justify-center"
          >
            <GitHubSVG width="24" height="24" />
          </a>
        </TooltipTrigger>
        <TooltipContent side="left">
          <p>Open GitHub repo</p>
        </TooltipContent>
      </Tooltip>
    </TooltipProvider>
  );
}

export function Thread() {
  const [threadId, setThreadId] = useQueryState("threadId");
  const [input, setInput] = useState("");
  const [firstTokenReceived, setFirstTokenReceived] = useState(false);
  const [activityOpen, setActivityOpen] = useState(false);

  const stream = useStreamContext();
  const messages = stream.messages;
  const isLoading = stream.isLoading;

  const lastError = useRef<string | undefined>(undefined);

  useEffect(() => {
    if (!stream.error) {
      lastError.current = undefined;
      return;
    }
    try {
      const message = (stream.error as any).message;
      if (!message || lastError.current === message) {
        // Message has already been logged. do not modify ref, return early.
        return;
      }

      // Message is defined, and it has not been logged yet. Save it, and send the error
      lastError.current = message;
      toast.error("An error occurred. Please try again.", {
        description: (
          <p>
            <strong>Error:</strong> <code>{message}</code>
          </p>
        ),
        richColors: true,
        closeButton: true,
      });
    } catch {
      // no-op
    }
  }, [stream.error]);

  // TODO: this should be part of the useStream hook
  const prevMessageLength = useRef(0);
  useEffect(() => {
    if (
      messages.length !== prevMessageLength.current &&
      messages?.length &&
      messages[messages.length - 1].type === "ai"
    ) {
      setFirstTokenReceived(true);
    }

    prevMessageLength.current = messages.length;
  }, [messages]);

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;
    setFirstTokenReceived(false);

    const newHumanMessage: Message = {
      id: uuidv4(),
      type: "human",
      content: input,
    };

    const toolMessages = ensureToolCallsHaveResponses(stream.messages);
    stream.submit(
      { messages: [...toolMessages, newHumanMessage] },
      {
        streamMode: ["values"],
        optimisticValues: (prev) => ({
          ...prev,
          messages: [
            ...(prev.messages ?? []),
            ...toolMessages,
            newHumanMessage,
          ],
        }),
      },
    );

    setInput("");
  };

  const handleRegenerate = (
    parentCheckpoint: Checkpoint | null | undefined,
  ) => {
    // Do this so the loading state is correct
    prevMessageLength.current = prevMessageLength.current - 1;
    setFirstTokenReceived(false);
    stream.submit(undefined, {
      checkpoint: parentCheckpoint,
      streamMode: ["values"],
    });
  };

  const chatStarted = !!threadId || !!messages.length;
  const hasNoAIOrToolMessages = !messages.find(
    (m) => m.type === "ai" || m.type === "tool",
  );

  return (
    <div className="orbit-shell orbit-workspace flex w-full h-screen overflow-hidden text-[#173b3b]">
      <motion.div
        className={cn(
          "flex-1 flex flex-col min-w-0 overflow-hidden relative",
          !chatStarted && "grid-rows-[1fr]",
        )}
        layout
      >
        {!chatStarted && (
          <div className="absolute top-0 left-0 w-full flex items-center justify-between gap-3 p-2 pl-4 z-10">
            <div className="absolute top-2 right-4 flex items-center">
              <OpenGitHubRepo />
            </div>
          </div>
        )}
        {chatStarted && (
          <div className="flex items-center justify-between gap-3 p-2 z-10 relative">
            <div className="flex items-center justify-start gap-2 relative">
              <motion.button
                className="flex gap-2 items-center cursor-pointer"
                onClick={() => setThreadId(null)}
              >
                <img className="orbit-logo-green orbit-workspace-logo" src="/images-removebg-preview.svg" alt="ORBIT" />
                  <span className="text-xl font-semibold tracking-tight text-[#173b3b]">
                  ORBIT Agent
                </span>
              </motion.button>
            </div>

            <div className="flex items-center gap-4">
              <div className="flex items-center">
                <OpenGitHubRepo />
              </div>
              <TooltipIconButton
                size="lg"
                className="p-4"
                tooltip="New thread"
                variant="ghost"
                onClick={() => setThreadId(null)}
              >
                <SquarePen className="size-5" />
              </TooltipIconButton>
            </div>

            <div className="absolute inset-x-0 top-full h-5 bg-linear-to-b from-background to-background/0" />
          </div>
        )}

        <StickToBottom className="relative flex-1 overflow-hidden">
          <StickyToBottomContent
            className={cn(
              "absolute px-4 inset-0 overflow-y-scroll [&::-webkit-scrollbar]:w-1.5 [&::-webkit-scrollbar-thumb]:rounded-full [&::-webkit-scrollbar-thumb]:bg-gray-300 [&::-webkit-scrollbar-track]:bg-transparent",
              !chatStarted && "flex flex-col items-stretch mt-[25vh]",
              chatStarted && "grid grid-rows-[1fr_auto]",
            )}
            contentClassName="pt-8 pb-16 max-w-4xl mx-auto flex flex-col gap-4 w-full"
            content={
              <>
                {messages
                  .filter((m) => !m.id?.startsWith(DO_NOT_RENDER_ID_PREFIX))
                  .map((message, index) =>
                    message.type === "human" ? (
                      <HumanMessage
                        key={message.id || `${message.type}-${index}`}
                        message={message}
                        isLoading={isLoading}
                      />
                    ) : (
                      <AssistantMessage
                        key={message.id || `${message.type}-${index}`}
                        message={message}
                        isLoading={isLoading}
                        handleRegenerate={handleRegenerate}
                      />
                    ),
                  )}
                {/* Special rendering case where there are no AI/tool messages, but there is an interrupt.
                    We need to render it outside of the messages list, since there are no messages to render */}
                {hasNoAIOrToolMessages && !!stream.interrupt && (
                  <AssistantMessage
                    key="interrupt-msg"
                    message={undefined}
                    isLoading={isLoading}
                    handleRegenerate={handleRegenerate}
                  />
                )}
                {isLoading && !firstTokenReceived && (
                  <AssistantMessageLoading />
                )}
              </>
            }
            footer={
              <div className="sticky flex flex-col items-center gap-3 bottom-0 border-t border-[#d9e6e2] bg-[#f4f8f6]/95 px-3 pt-3 backdrop-blur">
                {!chatStarted && (
                  <div className="orbit-empty-state">
                    <div className="orbit-empty-state__mark"><img className="orbit-logo-green" src="/images-removebg-preview.svg" alt="" /></div>
                    <span className="orbit-kicker">Conversation workspace</span>
                    <h1>What should Orbit look into?</h1>
                    <p>Ask about a document, request research, or ask Orbit to remember something.</p>
                    <div className="orbit-example-list">
                      {["What do my documents say about...", "Research..., then draft a roadmap", "Remember that..."].map((question) => <button key={question} onClick={() => setInput(question)}>{question}<span>↗</span></button>)}
                    </div>
                  </div>
                )}

                <ScrollToBottom className="absolute bottom-full left-1/2 -translate-x-1/2 mb-4 animate-in fade-in-0 zoom-in-95" />

                <div className="orbit-composer">
                  <form
                    onSubmit={handleSubmit}
                    className="grid grid-rows-[1fr_auto] gap-2 max-w-3xl mx-auto"
                  >
                    <textarea
                      value={input}
                      onChange={(e) => setInput(e.target.value)}
                      onKeyDown={(e) => {
                        if (
                          e.key === "Enter" &&
                          !e.shiftKey &&
                          !e.metaKey &&
                          !e.nativeEvent.isComposing
                        ) {
                          e.preventDefault();
                          const el = e.target as HTMLElement | undefined;
                          const form = el?.closest("form");
                          form?.requestSubmit();
                        }
                      }}
                      placeholder="Type your message..."
                      className="min-h-18 max-h-52 p-4 pb-1 border-none bg-transparent field-sizing-content shadow-none ring-0 outline-none focus:outline-none focus:ring-0 resize-y placeholder:text-[#72908b]"
                    />

                    <div className="orbit-composer__footer">
                      <p>Ask Orbit to remember something and it will propose a note for you to approve.</p>
                      {stream.isLoading ? (
                        <Button key="stop" onClick={() => stream.stop()}>
                          <LoaderCircle className="w-4 h-4 animate-spin" />
                          Cancel
                        </Button>
                      ) : (
                        <Button
                          type="submit"
                          className="transition-all shadow-md"
                          disabled={isLoading || !input.trim()}
                        >
                          Send
                        </Button>
                      )}
                    </div>
                  </form>
                </div>
              </div>
            }
          />
        </StickToBottom>
      </motion.div>
      <ActivityPanel
        messages={messages}
        isLoading={isLoading}
        open={activityOpen}
        onClose={() => setActivityOpen(false)}
      />
      <button
        className="orbit-activity-trigger"
        onClick={() => setActivityOpen((open) => !open)}
        aria-label="Toggle activity"
      >
        <Activity size={16} />
        <span>Activity</span>
      </button>
    </div>
  );
}
