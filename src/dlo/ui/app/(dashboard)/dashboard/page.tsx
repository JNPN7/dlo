'use client'

import { Header } from '@/components/layout';

import ReactGridLayout, { useContainerWidth } from "react-grid-layout";
import "react-grid-layout/css/styles.css";
import "react-resizable/css/styles.css";

function MyGrid() {
  const { width, containerRef, mounted } = useContainerWidth();

  const layout = [
    { i: "a", x: 0, y: 0, w: 1, h: 4, static: true },
    { i: "b", x: 1, y: 0, w: 10, h: 4 },
    { i: "c", x: 4, y: 0, w: 1, h: 4, minW: 2, maxW: 4 }
  ];

  return (
    <div ref={containerRef}>
      {mounted && (
        <ReactGridLayout
          layout={layout}
          width={width}
          gridConfig={{ cols: 12, rowHeight: 20 }}
          className="bg-purple-300"
        >
          <div key="a" className="bg-red-200 rounded flex justify-center items-center">A</div>
          <div key="b" className="bg-red-200 rounded flex justify-center items-center">B</div>
          <div key="c" className="bg-red-200 rounded flex justify-center items-center">C</div>
        </ReactGridLayout>
      )}
    </div>
  );
}

export default function DashboardPage() {
  return <div className="flex flex-col h-full">
    <Header
      title="Dashboards"
      description={`Dashboards available`}
    // onRefresh={() => refetch()}
    // isLoading={isLoading}
    />
    <MyGrid />

  </div>
}
