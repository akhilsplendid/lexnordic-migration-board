import { useCallback, useEffect, useState } from "react";

import { postWorkspace as postWorkspaceRequest, requestWorkspace, uploadWorkspaceDocument } from "../api/workspaceApi";
import { MATTER_NUMBER } from "../config";
import { fallbackWorkspace } from "../data/fallbackWorkspace";
import type { BusyAction, Workspace } from "../types";
import { messageFrom } from "../utils/workspace";

export function useWorkspace(matterNumber = MATTER_NUMBER, authToken: string | null, enabled = true) {
  const [workspace, setWorkspace] = useState<Workspace>(fallbackWorkspace);
  const [busyAction, setBusyAction] = useState<BusyAction>("loading");
  const [error, setError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);

  const loadWorkspace = useCallback(async () => {
    if (!enabled) return;
    setBusyAction((current) => current ?? "loading");
    try {
      const next = await requestWorkspace(`/matters/${matterNumber}/workspace`, authToken);
      setWorkspace(next);
      setError(next.backend_warning ?? null);
    } catch (caught) {
      setError(messageFrom(caught));
      setWorkspace(fallbackWorkspace);
    } finally {
      setBusyAction(null);
    }
  }, [authToken, enabled, matterNumber]);

  const postWorkspace = useCallback(async (path: string, action: Exclude<BusyAction, null>) => {
    if (!enabled) return;
    setBusyAction(action);
    setError(null);
    try {
      setWorkspace(await postWorkspaceRequest(path, authToken));
      setNotice(noticeForAction(action));
    } catch (caught) {
      setError(messageFrom(caught));
    } finally {
      setBusyAction(null);
    }
  }, [authToken, enabled]);

  const uploadFile = useCallback(async (file: File, documentType: string) => {
    if (!enabled) return;
    setBusyAction("upload");
    setError(null);
    try {
      setWorkspace(await uploadWorkspaceDocument(matterNumber, file, documentType, authToken));
      setNotice("Evidence uploaded and workspace updated.");
    } catch (caught) {
      setError(messageFrom(caught));
    } finally {
      setBusyAction(null);
    }
  }, [authToken, enabled, matterNumber]);

  useEffect(() => {
    void loadWorkspace();
  }, [loadWorkspace]);

  return {
    workspace,
    busyAction,
    error,
    notice,
    isBusy: busyAction !== null,
    clearNotice: () => setNotice(null),
    loadWorkspace,
    postWorkspace,
    uploadFile,
  };
}

function noticeForAction(action: Exclude<BusyAction, null>): string | null {
  if (action === "document-request") return "Document request checklist generated.";
  if (action === "agent-run") return "AI firm review completed for the active matter.";
  if (action === "approve") return "AI case packet finalized in this workspace.";
  if (action === "loading") return null;
  return "Workspace updated.";
}
