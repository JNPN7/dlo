import type { Column } from '@/types/manifest';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';

interface ColumnTableProps {
  columns: Column[];
}

export function ColumnTable({ columns }: ColumnTableProps) {
  if (columns.length === 0) {
    return (
      <div className="text-center py-8 text-muted-foreground">
        No columns defined
      </div>
    );
  }

  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Name</TableHead>
          <TableHead>Type</TableHead>
          <TableHead>Category</TableHead>
          <TableHead>Description</TableHead>
          <TableHead>Tags</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {columns.map((column) => (
          <TableRow key={column.name}>
            <TableCell className="font-medium">
              <code className="text-sm">{column.name}</code>
            </TableCell>
            <TableCell>
              <code className="text-xs bg-muted px-1.5 py-0.5 rounded">
                {column.type}
              </code>
            </TableCell>
            <TableCell>
              {column.category && (
                <Badge variant={column.category === 'dimension' ? 'secondary' : 'default'}>
                  {column.category}
                </Badge>
              )}
            </TableCell>
            <TableCell className="max-w-xs truncate text-muted-foreground">
              {column.description || '-'}
            </TableCell>
            <TableCell>
              <div className="flex gap-1 flex-wrap">
                {column.tags?.slice(0, 2).map((tag) => (
                  <Badge key={tag} variant="outline" className="text-xs">
                    {tag}
                  </Badge>
                ))}
                {column.tags && column.tags.length > 2 && (
                  <Badge variant="secondary" className="text-xs">
                    +{column.tags.length - 2}
                  </Badge>
                )}
              </div>
            </TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
}
