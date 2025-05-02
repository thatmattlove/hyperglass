declare global {
  namespace NodeJS {
    interface ProcessEnv {
      NODE_ENV: 'development' | 'production';
      CF_PAGES_BRANCH: string;
    }
  }
}
