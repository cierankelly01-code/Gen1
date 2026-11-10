/* Filled in at deploy time from build variables SUPABASE_URL and SUPABASE_ANON_KEY (see Dockerfile).
   This copy is for local work only. demo: true lets the forms show success without sending when no
   backend is set; the Dockerfile writes demo: false for the live site and refuses to build it without a backend. */
window.GENEX_CFG = { supabaseUrl: '', supabaseAnonKey: '', demo: true };
