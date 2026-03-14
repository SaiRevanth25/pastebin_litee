import { createBrowserRouter } from "react-router";
import CreatePaste from "./pages/CreatePaste";
import ViewPaste from "./pages/ViewPaste";
import SuccessPage from "./pages/SuccessPage";

export const router = createBrowserRouter([
  {
    path: "/",
    Component: CreatePaste,
  },
  {
    path: "/p/:id",
    Component: ViewPaste,
  },
  {
    path: "/success/:id",
    Component: SuccessPage,
  },
]);
