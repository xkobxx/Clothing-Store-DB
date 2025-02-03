import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"

export default function ExpandedSchemaExplanation() {
  return (
    <Card className="w-full max-w-3xl">
      <CardHeader>
        <CardTitle>Expanded Database Schema Explanation</CardTitle>
        <CardDescription>Justification of the expanded schema and its relationships</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <h3 className="text-lg font-semibold">Substantial Tables (5+)</h3>
        <ol className="list-decimal pl-6 space-y-2">
          <li>
            <strong>CUSTOMERS:</strong> Stores customer information
          </li>
          <li>
            <strong>ORDERS:</strong> Represents customer orders
          </li>
          <li>
            <strong>INVENTORY:</strong> Contains information about products
          </li>
          <li>
            <strong>EMPLOYEES:</strong> Stores employee data
          </li>
          <li>
            <strong>SUPPLIERS:</strong> Contains information about product suppliers
          </li>
        </ol>

        <h3 className="text-lg font-semibold">Additional Tables</h3>
        <ol className="list-decimal pl-6 space-y-2">
          <li>
            <strong>ORDER_ITEMS:</strong> Links orders to inventory items
          </li>
          <li>
            <strong>CATEGORIES:</strong> Stores product categories
          </li>
          <li>
            <strong>SIZES:</strong> Contains available sizes
          </li>
          <li>
            <strong>INVENTORY_SIZES:</strong> Links inventory items to sizes and quantities
          </li>
          <li>
            <strong>SHIFTS:</strong> Stores employee work shifts
          </li>
        </ol>

        <h3 className="text-lg font-semibold">Relationships and Referential Integrity Constraints</h3>
        <ul className="list-disc pl-6 space-y-2">
          <li>ORDERS.customer_id references CUSTOMERS.id (Many-to-One)</li>
          <li>ORDERS.employee_id references EMPLOYEES.id (Many-to-One)</li>
          <li>ORDER_ITEMS.order_id references ORDERS.id (Many-to-One)</li>
          <li>ORDER_ITEMS.inventory_id references INVENTORY.id (Many-to-One)</li>
          <li>INVENTORY.category_id references CATEGORIES.id (Many-to-One)</li>
          <li>INVENTORY.supplier_id references SUPPLIERS.id (Many-to-One)</li>
          <li>INVENTORY_SIZES.inventory_id references INVENTORY.id (Many-to-One)</li>
          <li>INVENTORY_SIZES.size_id references SIZES.id (Many-to-One)</li>
          <li>SHIFTS.employee_id references EMPLOYEES.id (Many-to-One)</li>
        </ul>

        <p>
          This expanded schema maintains 3NF while providing a more comprehensive structure for the clothing store
          database. It includes five substantial tables (CUSTOMERS, ORDERS, INVENTORY, EMPLOYEES, SUPPLIERS) and
          additional smaller tables to implement more complex relationships. The use of foreign keys ensures referential
          integrity across the database.
        </p>
      </CardContent>
    </Card>
  )
}

