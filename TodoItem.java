import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.ArrayList;
import java.util.Collection;
import java.util.Collections;
import java.util.List;
import java.util.Scanner;

/** TodoItem */
public class TodoItem implements Comparable<TodoItem> {

  protected String item;
  protected LocalDateTime createdAt;
  protected LocalDateTime planTime;
  DateTimeFormatter myFormatObj = DateTimeFormatter.ofPattern("dd-MM-yyyy HH:mm");

  public TodoItem(String item, LocalDateTime planAt) {
    this.item = item;
    this.createdAt = LocalDateTime.now();
    this.planTime = planAt;
  }

  public TodoItem() {
    this.item = null;
    this.createdAt = LocalDateTime.now();
    this.item = null;
  }

  public String getItem() {
    return item;
  }

  public LocalDateTime getCreatedAt() {
    return createdAt;
  }

  public LocalDateTime getPlanTime() {
    return planTime;
  }

  public void setCreatedAt(LocalDateTime createdAt) {
    this.createdAt = createdAt;
  }

  public void setItem(String item) {
    this.item = item;
  }

  public void setPlanTime(LocalDateTime planAt) {
    this.planTime = planAt;
  }

  @Override
  public String toString() {
    String formattedCreatedAt = this.createdAt.format(myFormatObj);
    String formattedPlanAt = (this.planTime != null) ? this.planTime.format(myFormatObj) : "Undecided";
    return "Item: "
        + this.item
        + "; Created at: "
        + formattedCreatedAt
        + "; Plan time: "
        + formattedPlanAt;
  }

  @Override
  public int compareTo(TodoItem o) {
    if (this.getPlanTime() == null) {
      return -1;
    }
    return this.getPlanTime().compareTo(o.getPlanTime());
  }

  public static void main(String[] args) {
    List<TodoItem> todoItemList = new ArrayList<>();
    Boolean keep = true;

    while (keep) {
      System.out
          .println("press 1 to view whole todo list, 2 to select one todo, 3 to change todo's time, 4 to change todo");
      Scanner scan = new Scanner(System.in);
      int command = scan.nextInt();
      if (command == 0) { // 0. add
        System.out.println("name of new todo list: ");
        String item = scan.nextLine();
        System.out.println("Please enter new plan time");
        int year = scan.nextInt();
        int month = scan.nextInt();
        int day = scan.nextInt();
        int hour = scan.nextInt();
        int minute = scan.nextInt();
        LocalDateTime plannedTime = LocalDateTime.of(year, month, day, hour, minute);
        TodoItem newTodoItem = new TodoItem(item, plannedTime);
        todoItemList.add(newTodoItem);
      } else if (command == 1) {// 1. 看全部todo
        String todoItemString = todoItemList.toString();
        System.out.println(todoItemString);
      } else if (command == 2) {// 2. 看单个todo
        System.out.println("Which todo would you like to view?");
        int index = scan.nextInt();
        String todo = todoItemList.get(index).toString();
        System.out.println(todo);
      } else if (command == 3) {// 3. 更改todo 时间 并且重新sort
        System.out.println("Which todo's time would you want to change?");
        int index = scan.nextInt();
        System.out.println("Please enter new plan time");
        int year = scan.nextInt();
        int month = scan.nextInt();
        int day = scan.nextInt();
        int hour = scan.nextInt();
        int minute = scan.nextInt();
        LocalDateTime plannedTime = LocalDateTime.of(year, month, day, hour, minute);
        todoItemList.get(index).setPlanTime(plannedTime);
        Collections.sort(todoItemList);
        System.out.println(todoItemList);
      } else if (command == 4) {// 4. 更改todo 名字
        System.out.println("Which todo's name would you want to change?");
        int index = scan.nextInt();
        System.out.println("Change to?");
        String name = scan.nextLine();
        todoItemList.get(index).setItem(name);
      }
      System.out.println("Continue? yes/no");
      String response = scan.nextLine();
      if (response == "no") {
        keep = false;
      }
      scan.close();
    }
  }
}
