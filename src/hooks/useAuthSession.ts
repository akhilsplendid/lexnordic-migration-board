import type { Session, User } from "@supabase/supabase-js";
import { useEffect, useMemo, useState } from "react";

import { isSupabaseAuthConfigured, supabase } from "../lib/supabaseClient";

export function useAuthSession() {
  const [session, setSession] = useState<Session | null>(null);
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let mounted = true;
    if (!supabase) {
      setIsLoading(false);
      return;
    }

    supabase.auth.getSession().then(({ data, error: sessionError }) => {
      if (!mounted) return;
      if (sessionError) setError(sessionError.message);
      setSession(data.session ?? null);
      setUser(data.session?.user ?? null);
      setIsLoading(false);
    });

    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange((_event, nextSession) => {
      setSession(nextSession);
      setUser(nextSession?.user ?? null);
    });

    return () => {
      mounted = false;
      subscription.unsubscribe();
    };
  }, []);

  const accessToken = session?.access_token ?? null;

  return useMemo(
    () => ({
      accessToken,
      error,
      isConfigured: isSupabaseAuthConfigured,
      isLoading,
      message,
      session,
      user,
      clearMessage: () => setMessage(null),
      signIn: async (email: string, password: string) => {
        if (!supabase) return;
        setError(null);
        setMessage(null);
        const { error: signInError } = await supabase.auth.signInWithPassword({ email, password });
        if (signInError) setError(signInError.message);
      },
      signOut: async () => {
        if (!supabase) return;
        await supabase.auth.signOut();
      },
      signUp: async (email: string, password: string) => {
        if (!supabase) return;
        setError(null);
        setMessage(null);
        const { data, error: signUpError } = await supabase.auth.signUp({ email, password });
        if (signUpError) {
          setError(signUpError.message);
          return;
        }
        if (!data.session) {
          setMessage("Check your email to confirm the account, then sign in.");
        }
      },
    }),
    [accessToken, error, isLoading, message, session, user],
  );
}
