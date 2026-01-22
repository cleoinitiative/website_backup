# Types of Cell References

> Source: https://edu.gcfglobal.org/en/googlespreadsheets/types-of-cell-references/1/

## Lesson 14: Types of Cell References

/en/googlespreadsheets/creating-complex-formulas/content/

## Introduction

There are two types of cell references: relative and absolute. Relative and absolute references behave differently when copied and filled to other cells. Relative references change when a formula is copied to another cell. Absolute references, on the other hand, remain constant no matter where they are copied.

Watch the video below to learn how to use relative and absolute references.

## Relative references

By default, all cell references are relative references. When copied across multiple cells, they change based on the relative position of rows and columns. For example, if you copy the formula =A1+B1 from row 1 to row 2, the formula will become =A2+B2. Relative references are especially convenient whenever you need to repeat the same calculation across multiple rows or columns.

## To create and copy a formula using relative references:

In the following example, we want to create a formula that will multiply each item's price by the quantity. Instead of creating a new formula for each row, we can create a single formula in cell D4 and then copy it to the other rows. We'll use relative references so the formula calculates the total for each item correctly.

- Select the cell that will contain the formula. In our example, we'll select cell D4.

- Enter the formula to calculate the desired value. In our example, we'll type=B4*C4.

- Press Enter on your keyboard. The formula will be calculated, and the result will be displayed in the cell.

- Select the cell you want to copy. In our example, we'll select cell D4. The fill handle will appear in the bottom-right corner of the cell.

- Click and drag the fill handle over the cells you want to fill. In our example, we'll select cells D5:D13.

- Release the mouse. The formula will be copied to the selected cells with relative references, displaying the result in each cell.

You can double-click the filled cells to check their formulas for accuracy. The relative cell references should be different for each cell, depending on their rows.

## Absolute references

There may be times when you do not want a cell reference to change when copying or filling cells. You can use an absolute reference to keep a row and/or column constant in the formula.

An absolute reference is designated in the formula by the addition of a dollar sign ($). It can precede the column reference, the row reference, or both.

You will most likely use the $A$2 format when creating formulas that contain absolute references. The other two formats are used much less often.

## To create and copy a formula using absolute references:

In the example below, we're going to use cell E2 (which contains the tax rate at 7.5%) to calculate the sales tax for each item in column D. To make sure the reference to the tax rate stays constant—even when the formula is copied and filled to other cells—we'll need to make cell $E$2 an absolute reference.

- Select the cell that will contain the formula. In our example, we'll select cell D4.

- Enter the formula to calculate the desired value. In our example, we'll type =(B4*C4)*$E$2, making $E$2 an absolute reference.

- Press Enter on your keyboard. The formula will calculate, and the result will display in the cell.

- Select the cell you want to copy. In our example, we'll select cell D4. The fill handle will appear in the bottom-right corner of the cell.

- Click and drag the fill handle over the cells you want to fill (cells D5:D13 in our example).

- Release the mouse. The formula will be copied to the selected cells with an absolute reference, and the values will be calculated in each cell.

You can double-click the filled cells to check their formulas for accuracy. The absolute reference should be the same for each cell, while the other references are relative to the cell's row.

Be sure to include the dollar sign ($) whenever you're making an absolute reference across multiple cells. Without the dollar sign, Google Sheets will interpret it as a relative reference, producing an incorrect result when copied to other cells.

## Challenge!

- Open our example file. Make sure you're signed in to Google, then click File > Make a copy.

- Select the Challenge sheet.

- In cell D4, create a formula that would calculate how much the customer would save on each item by multiplying the unit price, quantity, and discount shown in cell E2.

- Use the fill handle to copy the formula you created in step 3 to cells D5:D12.

- When you're finished, your spreadsheet should look something like this:

/en/googlespreadsheets/working-with-functions/content/