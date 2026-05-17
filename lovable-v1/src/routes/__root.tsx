import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import {
  Outlet,
  Link,
  createRootRouteWithContext,
  useRouter,
  HeadContent,
  Scripts,
} from "@tanstack/react-router";

import appCss from "../styles.css?url";

function NotFoundComponent() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-background px-4">
      <div className="max-w-md text-center">
        <h1 className="font-serif text-7xl">404</h1>
        <p className="mt-2 text-sm text-ink-muted">页面不存在</p>
        <Link to="/" className="mt-6 inline-flex h-10 items-center rounded-lg bg-ink px-4 text-sm text-background">回到首页</Link>
      </div>
    </div>
  );
}

function ErrorBoundary({ error, reset }: { error: Error; reset: () => void }) {
  const router = useRouter();
  console.error(error);
  return (
    <div className="flex min-h-screen items-center justify-center bg-background px-4">
      <div className="max-w-md text-center">
        <h1 className="font-serif text-2xl">出错了</h1>
        <p className="mt-2 text-sm text-ink-muted">{error.message}</p>
        <button onClick={() => { router.invalidate(); reset(); }} className="mt-6 inline-flex h-10 items-center rounded-lg bg-ink px-4 text-sm text-background">重试</button>
      </div>
    </div>
  );
}

export const Route = createRootRouteWithContext<{ queryClient: QueryClient }>()({
  head: () => ({
    meta: [
      { charSet: "utf-8" },
      { name: "viewport", content: "width=device-width, initial-scale=1" },
      { title: "ReviewResponseAssistant · 审稿意见回复助手" },
      { name: "description", content: "为研究生与青年研究者打造的审稿意见回复工具原型设计" },
      { property: "og:title", content: "ReviewResponseAssistant · 审稿意见回复助手" },
      { name: "twitter:title", content: "ReviewResponseAssistant · 审稿意见回复助手" },
      { property: "og:description", content: "为研究生与青年研究者打造的审稿意见回复工具原型设计" },
      { name: "twitter:description", content: "为研究生与青年研究者打造的审稿意见回复工具原型设计" },
      { property: "og:image", content: "https://pub-bb2e103a32db4e198524a2e9ed8f35b4.r2.dev/19b35a70-579b-4427-8947-30e7a8d7ddd2/id-preview-d0be1456--03baf7b4-1966-40e9-856e-2e16ab6e9ccf.lovable.app-1778927673985.png" },
      { name: "twitter:image", content: "https://pub-bb2e103a32db4e198524a2e9ed8f35b4.r2.dev/19b35a70-579b-4427-8947-30e7a8d7ddd2/id-preview-d0be1456--03baf7b4-1966-40e9-856e-2e16ab6e9ccf.lovable.app-1778927673985.png" },
      { name: "twitter:card", content: "summary_large_image" },
      { property: "og:type", content: "website" },
    ],
    links: [
      { rel: "stylesheet", href: appCss },
      { rel: "preconnect", href: "https://fonts.googleapis.com" },
      { rel: "preconnect", href: "https://fonts.gstatic.com", crossOrigin: "" },
      { rel: "stylesheet", href: "https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" },
    ],
  }),
  shellComponent: RootShell,
  component: () => (
    <QueryProviders>
      <Outlet />
    </QueryProviders>
  ),
  notFoundComponent: NotFoundComponent,
  errorComponent: ErrorBoundary,
});

function QueryProviders({ children }: { children: React.ReactNode }) {
  const { queryClient } = Route.useRouteContext();
  return <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>;
}

function RootShell({ children }: { children: React.ReactNode }) {
  return (
    <html lang="zh-CN">
      <head><HeadContent /></head>
      <body>{children}<Scripts /></body>
    </html>
  );
}
